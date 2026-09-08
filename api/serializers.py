from rest_framework import serializers
from Tour.models import (
    Country, DepartureCity, GoalCity, TourOperator,
    Hotel, HotelPhoto, Tour, BookingRequest,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code"]


class DepartureCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartureCity
        fields = ["id", "name"]


class GoalCitySerializer(serializers.ModelSerializer):
    country = serializers.IntegerField(source="country_id", allow_null=True)

    class Meta:
        model = GoalCity
        fields = ["id", "name", "country"]


class TourOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourOperator
        fields = ["id", "name"]


class TourListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="hotel.name")
    stars = serializers.IntegerField(source="hotel.stars")
    country = serializers.CharField(source="hotel.country.name", default="")
    resort = serializers.CharField(source="hotel.resort", default="")
    img = serializers.SerializerMethodField()
    meal = serializers.CharField(source="get_meal_type_display")
    price = serializers.SerializerMethodField()

    departure_city = serializers.CharField(source="departure_city.name", default=None)
    goal_city = serializers.CharField(source="goal_city.name", default=None)
    tour_operator = serializers.CharField(source="tour_operator.name", default=None)

    class Meta:
        model = Tour
        fields = [
            "id", "name", "stars", "nights", "country", "resort", "meal", "price", "img",
            "is_hot", "departure_city", "goal_city", "tour_operator",
            "departure_date", "adults_count", "children",
        ]

    def get_img(self, obj):
        photo = obj.hotel.photos.first()
        request = self.context.get("request")
        if photo and request:
            return request.build_absolute_uri(photo.image.url)
        return None

    def get_price(self, obj):
        return f"{obj.price_amount} {obj.get_price_currency_display()}"


class TourDetailSerializer(TourListSerializer):
    description = serializers.CharField(source="hotel.description")
    photos = serializers.SerializerMethodField()

    class Meta(TourListSerializer.Meta):
        fields = TourListSerializer.Meta.fields + ["description", "photos"]

    def get_photos(self, obj):
        request = self.context.get("request")
        return [
            request.build_absolute_uri(p.image.url) if request else p.image.url
            for p in obj.hotel.photos.all()
        ]


class BookingRequestSerializer(serializers.ModelSerializer):
    tour_name = serializers.CharField(write_only=True, required=False)
    contact_channel = serializers.ChoiceField(
        choices=[("viber", "Viber"), ("telegram", "Telegram")],
        write_only=True, required=False,
    )

    class Meta:
        model = BookingRequest
        fields = ["id", "tour", "tour_name", "full_name", "phone", "email",
                    "comment", "contact_channel", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def create(self, validated_data):
        validated_data.pop("tour_name", None)
        channel = validated_data.pop("contact_channel", None)
        if channel:
            comment = validated_data.get("comment", "")
            validated_data["comment"] = f"{comment}\n[Канал зв'язку: {channel}]".strip()
        return super().create(validated_data)