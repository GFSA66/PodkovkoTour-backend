from rest_framework import serializers

from Tour.models import (
    BookingRequest,
    Country,
    DepartureCity,
    GoalCity,
    HotelPhoto,
    Review,
    Tour,
    TourOperator,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name", "code")


class DepartureCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartureCity
        fields = ("id", "name")


class GoalCitySerializer(serializers.ModelSerializer):
    # Віддаємо id країни напряму (не вкладеним об'єктом) — фронт звіряє його
    # з countryId, щоб зв'язати селекти "Країна" і "Курорт/місто" між собою.
    country = serializers.IntegerField(source="country_id", allow_null=True)

    class Meta:
        model = GoalCity
        fields = ("id", "name", "country")


class TourOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourOperator
        fields = ("id", "name")


class HotelPhotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = HotelPhoto
        fields = ("id", "image", "order")

    def get_image(self, obj):
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class TourListSerializer(serializers.ModelSerializer):
    """Форма узгоджена з фронтом (App.tsx): name/stars/country/meal/price/img
    замість "сирих" полів hotel_* — щоб не переписувати фронт під бекенд."""

    name = serializers.CharField(source="hotel.name")
    stars = serializers.IntegerField(source="hotel.stars")
    country = serializers.CharField(source="hotel.country.name", default="")
    resort = serializers.CharField(source="hotel.resort", default="")
    meal = serializers.CharField(source="get_meal_type_display")
    price = serializers.SerializerMethodField()
    img = serializers.SerializerMethodField()

    # Ці три поля повертають ІМ'Я довідника (не id) — саме так їх звіряє
    # applyFilters() на фронті з обраним у селекті значенням.
    departure_city = serializers.CharField(source="departure_city.name", default=None)
    goal_city = serializers.CharField(source="goal_city.name", default=None)
    tour_operator = serializers.CharField(source="tour_operator.name", default=None)

    class Meta:
        model = Tour
        fields = (
            "id", "name", "stars", "nights", "country", "resort", "meal", "price", "img",
            "is_hot", "status", "departure_city", "goal_city", "tour_operator",
            "departure_date", "adults_count", "children",
        )

    def get_price(self, obj):
        return f"{obj.price_amount} {obj.get_price_currency_display()}"

    def get_img(self, obj):
        photo = obj.hotel.photos.first()
        if not photo:
            return None
        request = self.context.get("request")
        url = photo.image.url
        return request.build_absolute_uri(url) if request else url


class TourDetailSerializer(TourListSerializer):
    """Повна форма для сторінки туру — опис готелю + вся галерея фото."""

    description = serializers.CharField(source="hotel.description")
    photos = serializers.SerializerMethodField()

    class Meta(TourListSerializer.Meta):
        fields = TourListSerializer.Meta.fields + ("description", "photos")

    def get_photos(self, obj):
        request = self.context.get("request")
        return [
            request.build_absolute_uri(p.image.url) if request else p.image.url
            for p in obj.hotel.photos.all()
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "author_name", "rating", "text", "created_at")

class BookingRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = (
            "id",
            "tour",
            "full_name",
            "phone",
            "email",
            "comment",
            "preferred_date_from",
            "preferred_date_to",
            "adults_count",
            "children",
            "nights",
            "meal_type",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "adults_count": {"required": False},
            "children": {"required": False},
            "nights": {"required": False},
            "meal_type": {"required": False, "allow_blank": True},
        }