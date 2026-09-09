from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    # Без цього поля avatar просто не потрапляє у відповідь /auth/me/,
    # /auth/register/, /auth/login/ і /auth/profile/ — фронтенд не бачив би,
    # що аватар взагалі є.
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("email", "full_name", "phone", "avatar", "is_staff")


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Користувач з такою поштою вже існує.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(email=validated_data["email"], password=validated_data["password"])


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # Django ожидает kwarg "username" даже когда USERNAME_FIELD = "email" —
        # ModelBackend сам подставит его в фильтр по нужному полю.
        user = authenticate(self.context["request"], username=attrs["email"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Невірна пошта або пароль.")
        attrs["user"] = user
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    # Без цього поля PATCH /auth/profile/ мовчки ІГНОРУЄ файл avatar у
    # multipart-запиті — не падає з помилкою, просто нічого не зберігає.
    # Це і є причина, чому завантаження фото зараз нічого не робить.
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("full_name", "phone", "avatar")