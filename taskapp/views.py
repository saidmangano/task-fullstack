from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter

import jwt

from .models import Task, User
from .permissions import TaskAccessPermission
from .serializers import LoginSerializer, RegisterSerializer, TaskSerializer, UserSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("created_by", "assigned_to")
    serializer_class = TaskSerializer
    permission_classes = [TaskAccessPermission]
    filter_backends = [OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Task.objects.none()

        queryset = Task.objects.select_related("created_by", "assigned_to")
        if user.role == User.Role.CLIENT:
            queryset = queryset.filter(created_by=user)

        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset

    @action(detail=False, methods=["get"])
    def my(self, request):
        queryset = Task.objects.filter(created_by=request.user)
        status_value = request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)
        queryset = queryset.order_by(*self.ordering)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {"user_id": user.id, "email": user.email}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        return Response({"token": token})
