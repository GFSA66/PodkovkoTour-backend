from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .forms import UserChangeForm, UserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = (
        "avatar_preview",
        "email",
        "full_name",
        "phone",
        "is_staff",
        "is_active",
        "past_tours_count",
    )
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("email", "full_name", "phone")
    ordering = ("email",)
    filter_horizontal = ("past_tours", "groups", "user_permissions")
    readonly_fields = ("avatar_preview_large", "last_login", "date_joined")
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Профиль", {"fields": ("full_name", "phone", "avatar", "avatar_preview_large")}),
        ("История", {"fields": ("past_tours",)}),
        ("Права доступа", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Даты", {"fields": ("last_login", "date_joined"), "classes": ("collapse",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )

    @admin.display(description="")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:36px;width:36px;border-radius:50%;object-fit:cover;" />',
                obj.avatar.url,
            )
        return format_html(
            '<span style="display:inline-flex;align-items:center;justify-content:center;'
            'height:36px;width:36px;border-radius:50%;background:#444;color:#fff;font-size:13px;">{}</span>',
            (obj.full_name or obj.email)[:1].upper(),
        )

    @admin.display(description="Аватар")
    def avatar_preview_large(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:140px;width:140px;border-radius:12px;object-fit:cover;" />',
                obj.avatar.url,
            )
        return "—"

    @admin.display(description="Туров в истории")
    def past_tours_count(self, obj):
        return obj.past_tours.count()