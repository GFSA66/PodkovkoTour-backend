from django.conf import settings
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, blank=True)  # ISO, напр. "TR"

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class DepartureCity(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Дніпро, Кишинів...

    def __str__(self):
        return self.name

class GoalCity(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Дніпро, Кишинів...
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="goal_cities", null=True, blank=True)

    def __str__(self):
        return self.name


class TourOperator(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Join Up, Kompas, Alf.ua

    def __str__(self):
        return self.name


class Hotel(models.Model):
    class Stars(models.IntegerChoices):
        THREE = 3, "3*"
        FOUR = 4, "4*"
        FIVE = 5, "5*"

    name = models.CharField(max_length=200)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="hotels", null=True, blank=True)
    goal_city = models.ForeignKey(GoalCity, on_delete=models.PROTECT, related_name="hotels", null=True, blank=True)
    resort = models.CharField(max_length=150, blank=True)  # Аланія, Золоті Піски...
    stars = models.PositiveSmallIntegerField(choices=Stars.choices, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_stars_display() or '-'})"


class HotelPhoto(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="hotels/%Y/%m/")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class Tour(models.Model):
    class MealType(models.TextChoices):
        RO = "RO", "Без харчування"
        BB = "BB", "Сніданок"
        HB = "HB", "Сніданок і вечеря"
        FB = "FB", "Повний пансіон"
        AI = "AI", "Все включено"
        UAI = "UAI", "Ультра все включено"

    class Currency(models.TextChoices):
        UAH = "UAH", "₴"
        USD = "USD", "$"
        EUR = "EUR", "€"

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        ACTIVE = "active", "Активен"
        SOLD_OUT = "sold_out", "Мест нет"
        EXPIRED = "expired", "Не актуален"

    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT, related_name="tours")
    tour_operator = models.ForeignKey(TourOperator, on_delete=models.PROTECT, related_name="tours", null=True, blank=True)
    departure_city = models.ForeignKey(DepartureCity, on_delete=models.PROTECT, related_name="tours")
    goal_city = models.ForeignKey(GoalCity, on_delete=models.PROTECT, related_name="tours", null=True, blank=True)

    departure_date = models.DateField(null=True, blank=True)
    nights = models.PositiveSmallIntegerField()
    adults_count = models.PositiveSmallIntegerField(default=2)
    children = models.BooleanField(default=False)  # есть ли дети в туре
    meal_type = models.CharField(max_length=3, choices=MealType.choices)

    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.UAH)

    is_hot = models.BooleanField(default=False)  # "горящий" тур — 🔥 в Telegram
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    # задел на этап 2: автоимпорт из IT-Tour вместо ручного ввода
    source = models.CharField(max_length=20, default="manual")  # manual | it_tour_api
    external_id = models.CharField(max_length=100, blank=True, null=True, unique=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="tours_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_hot", "departure_date"]
        indexes = [
            models.Index(fields=["hotel", "departure_date"]),
            models.Index(fields=["is_hot", "status"]),
            models.Index(fields=["price_amount"]),
        ]

    def __str__(self):
        return f"{self.hotel} — {self.departure_date} ({self.nights} ноч.)"


class BookingRequest(models.Model):
    class PreferredContact(models.TextChoices):
        VIBER = "viber", "Viber"
        TELEGRAM = "telegram", "Telegram"
        
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        CONFIRMED = "confirmed", "Подтверждена"
        CANCELLED = "cancelled", "Отменена"

    preferred_contact = models.CharField(max_length=10, choices=PreferredContact.choices, default=PreferredContact.TELEGRAM)
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, related_name="booking_requests")
    adults_count = models.PositiveSmallIntegerField(default=2)
    children = models.BooleanField(default=False)  # есть ли дети в туре
    nights = models.PositiveSmallIntegerField(blank=True, null=True)  # на случай, если тур не выбран (только даты)
    meal_type = models.CharField(max_length=3, choices=Tour.MealType.choices, blank=True)  # на случай, если тур не выбран (только даты)
    preferred_date_from = models.DateField(null=True, blank=True)
    preferred_date_to = models.DateField(null=True, blank=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    comment = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="booking_requests",
    )

    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_requests"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заявка от {self.full_name} ({self.get_status_display()})"


class Review(models.Model):
    author_name = models.CharField(max_length=150)
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1-5
    text = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    author_avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True, null=True)

    def __str__(self):
        return f"{self.author_name} — {self.rating}/5"
    is_published = models.BooleanField(default=False)
    is_pinned = models.BooleanField(
        default=False,
        help_text="Показувати цей відгук у блоці «Про турагента» на головній (макс. 3)",
    )