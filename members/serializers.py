from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        try:
            user = User.objects.get(email__iexact=self.validated_data["email"])
        except User.DoesNotExist:
            return  # тихо молчимо — не розкриваємо, чи є така пошта в базі

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password/{uid}/{token}/"
        send_mail(
            subject="Відновлення пароля",
            message=f"Для відновлення пароля перейдіть за посиланням:\n{reset_link}\n\nЯкщо ви не запитували відновлення — ігноруйте цей лист.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Паролі не співпадають."})
        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(attrs["uid"])))
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError({"uid": "Недійсне посилання."})
        if not token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "Посилання недійсне або застаріле."})
        validate_password(attrs["new_password"], user=user)
        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


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
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Користувач з такою поштою вже існує.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data.get("phone", ""),
        )


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