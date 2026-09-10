from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ("id", "author_name", "rating", "text", "created_at", "author_avatar")

    def get_author_avatar(self, obj):
        if not obj.author_avatar:
            return None
        request = self.context.get("request")
        url = obj.author_avatar.url
        return request.build_absolute_uri(url) if request else url

class ReviewCreateSerializer(serializers.ModelSerializer):
    """Для POST — приймає лише rating + text, решту (автор, tour,
    is_published) підставляє view. is_published свідомо не в fields —
    користувач не може сам себе опублікувати."""

    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ("rating", "text")

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        author_name = getattr(user, "full_name", "") or user.email
        author_avatar = getattr(user, "avatar", None)
        return Review.objects.create(
            tour_id=self.context["tour_id"],
            author_name=author_name,
            author_avatar=author_avatar,
            rating=validated_data["rating"],
            text=validated_data["text"],
            is_published=False,  # публікує менеджер вручну через адмінку
        )