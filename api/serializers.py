from rest_framework import serializers

from Tour.models import BookingRequest, Tour


class TourListSerializer(serializers.ModelSerializer):
    """Формат карточки тура — под интерфейс Tour во фронтенде."""

    name = serializers.CharField(source="hotel.name")
    stars = serializers.IntegerField(source="hotel.stars")
    country = serializers.CharField(source="hotel.country.name")
    meal = serializers.CharField(source="get_meal_type_display")
    price = serializers.SerializerMethodField()
    img = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = ["id", "name", "stars", "nights", "country", "meal", "price", "img", "is_hot"]

    def get_price(self, obj):
        symbol = {"UAH": "₴", "USD": "$", "EUR": "€"}.get(obj.price_currency, "")
        return f"від {obj.price_amount:,.0f} {symbol}".replace(",", " ")

    def get_img(self, obj):
        photo = obj.hotel.photos.first()
        if not photo:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(photo.image.url) if request else photo.image.url


class TourDetailSerializer(TourListSerializer):
    """Расширенная версия — для страницы тура: описание + все фото галереи."""

    description = serializers.CharField(source="hotel.description")
    photos = serializers.SerializerMethodField()

    class Meta(TourListSerializer.Meta):
        fields = TourListSerializer.Meta.fields + ["description", "photos"]

    def get_photos(self, obj):
        request = self.context.get("request")
        urls = [p.image.url for p in obj.hotel.photos.all()]
        if request:
            urls = [request.build_absolute_uri(u) for u in urls]
        return urls


class BookingRequestCreateSerializer(serializers.ModelSerializer):
    """
    Заявка из формы бронирования на сайте.
    tour_name и contact_channel — служебные поля с фронта, не хранятся как
    отдельные колонки, а уходят в comment, чтобы не плодить миграции ради мелочи.
    """

    tour_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    contact_channel = serializers.ChoiceField(
        choices=["viber", "telegram"], write_only=True, required=False
    )

    class Meta:
        model = BookingRequest
        fields = ["id", "tour", "full_name", "phone", "email", "comment", "tour_name", "contact_channel"]
        extra_kwargs = {"tour": {"required": False, "allow_null": True}}

    def create(self, validated_data):
        tour_name = validated_data.pop("tour_name", "")
        channel = validated_data.pop("contact_channel", "")
        note = f"Бажаний контакт: {channel or '—'}"
        if tour_name:
            note = f"Тур: {tour_name}. {note}"
        validated_data["comment"] = (validated_data.get("comment") or note)
        return super().create(validated_data)
