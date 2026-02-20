from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LoginView, ProfileView, RegisterView, TaskViewSet

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
