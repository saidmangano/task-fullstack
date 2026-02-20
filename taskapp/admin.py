from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Task, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "email", "username", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_by", "assigned_to", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description", "created_by__email", "assigned_to__email")
