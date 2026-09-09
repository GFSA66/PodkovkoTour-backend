from django.contrib.auth import login as django_login, logout as django_logout
from django.middleware.csrf import get_token
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from members.serializers import (
    LoginSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)


class CsrfCookieView(APIView):
    """GET /api/auth/csrf/ — дергается фронтом один раз при старте,
    чтобы в браузере появилась csrftoken cookie для последующих POST/PATCH."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        get_token(request)
        return Response({"detail": "CSRF cookie set"})


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        django_login(request, user)
        # context={"request": request} — щоб avatar (поки що порожній) і
        # надалі серіалізувався абсолютним URL, а не відносним шляхом.
        return Response(UserSerializer(user, context={"request": request}).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        return Response(UserSerializer(user, context={"request": request}).data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        django_logout(request)
        return Response({"detail": "Вихід виконано"})


class MeView(APIView):
    """GET /api/auth/me/ — 200 + дані юзера, якщо залогінений; 401, якщо гість."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Не авторизовано"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(UserSerializer(request.user, context={"request": request}).data)


class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user, context={"request": request}).data)


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        django_logout(request)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)