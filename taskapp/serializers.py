from rest_framework import serializers

from .models import Task, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role", "first_name", "last_name"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=1)


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "created_by",
            "assigned_to",
        ]
        read_only_fields = ["created_at", "created_by"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return attrs

        if self.instance and "status" in attrs:
            if self.instance.status in [Task.Status.DONE, Task.Status.REJECTED]:
                raise serializers.ValidationError(
                    {"status": "Изменить статус после завершения или отклонения невозможно."}
                )

        if "status" in attrs:
            new_status = attrs["status"]

            if user.role == User.Role.CLIENT:
                raise serializers.ValidationError(
                    {"status": "Клиенту не разрешается менять статус.."}
                )

            if new_status == Task.Status.APPROVED and user.role != User.Role.MODERATOR:
                raise serializers.ValidationError(
                    {"status": "Только модератор может установить статус «одобрено».."}
                )

            if new_status == Task.Status.DONE:
                if not self.instance:
                    raise serializers.ValidationError(
                        {"status": "Назначенный пользователь может установить статус «выполнено» только для существующих задач."}
                    )
                if self.instance.assigned_to_id != user.id:
                    raise serializers.ValidationError(
                        {"status": "Только owner пользователь может устанавливать статус 'Выполнено'."})

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["created_by"] = request.user
        return super().create(validated_data)
