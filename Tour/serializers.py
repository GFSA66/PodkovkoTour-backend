from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    # На головній відгук не прив'язаний візуально до конкретного туру, але
    # tour_name корисно показати як контекст ("відгук про тур «...»").
    # allow_null/required=False — бо Review.tour може бути null.
    tour_name = serializers.CharField(source="tour.name", read_only=True, required=False, default=None)

    class Meta:
        model = Review
        fields = ("id", "author_name", "rating", "text", "created_at", "tour_name")

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
        return Review.objects.create(
            tour_id=self.context["tour_id"],
            author_name=author_name,
            rating=validated_data["rating"],
            text=validated_data["text"],
            is_published=False,  # публікує менеджер вручну через адмінку
        )