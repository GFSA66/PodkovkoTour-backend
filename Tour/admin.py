from django.contrib import admin
from .models import Tour
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Country,
    DepartureCity,
    TourOperator,
    Hotel,
    HotelPhoto,
    Tour,
    BookingRequest,
    Review,
)


# ---------------------------------------------------------------------------
# Справочники
# ---------------------------------------------------------------------------

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "hotels_count")
    search_fields = ("name", "code")
    ordering = ("name",)

    @admin.display(description="Отелей")
    def hotels_count(self, obj):
        return obj.hotels.count()


@admin.register(DepartureCity)
class DepartureCityAdmin(admin.ModelAdmin):
    list_display = ("name", "tours_count")
    search_fields = ("name",)

    @admin.display(description="Туров")
    def tours_count(self, obj):
        return obj.tours.count()


@admin.register(TourOperator)
class TourOperatorAdmin(admin.ModelAdmin):
    list_display = ("name", "tours_count")
    search_fields = ("name",)

    @admin.display(description="Туров")
    def tours_count(self, obj):
        return obj.tours.count()


# ---------------------------------------------------------------------------
# Отели
# ---------------------------------------------------------------------------

class HotelPhotoInline(admin.TabularInline):
    model = HotelPhoto
    extra = 1
    fields = ("preview", "image", "order")
    readonly_fields = ("preview",)

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:6px;object-fit:cover;" />',
                obj.image.url,
            )
        return "—"


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "country",
        "resort",
        "stars_display",
        "is_active",
        "photos_count",
        "tours_count",
    )
    list_filter = ("country", "stars", "is_active")
    search_fields = ("name", "resort")
    list_editable = ("is_active",)
    inlines = [HotelPhotoInline]
    fieldsets = (
        (None, {"fields": ("name", "country", "resort", "stars", "is_active")}),
        ("Описание", {"fields": ("description",), "classes": ("collapse",)}),
    )

    @admin.display(description="Звёзды", ordering="stars")
    def stars_display(self, obj):
        if not obj.stars:
            return "—"
        return format_html('<span style="color:#f5a623;">{}</span>', "★" * obj.stars)

    @admin.display(description="Фото")
    def photos_count(self, obj):
        return obj.photos.count()

    @admin.display(description="Туров")
    def tours_count(self, obj):
        return obj.tours.count()


# ---------------------------------------------------------------------------
# Туры
# ---------------------------------------------------------------------------

STATUS_COLORS = {
    Tour.Status.DRAFT: "#9e9e9e",
    Tour.Status.ACTIVE: "#43a047",
    Tour.Status.SOLD_OUT: "#e53935",
    Tour.Status.EXPIRED: "#757575",
}


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        "hotel_link",
        "tour_operator",
        "departure_city",
        "departure_date",
        "nights",
        "meal_type",
        "price_display",
        "hot_badge",
        "status_badge",
        "source",
    )
    list_filter = (
        "status",
        "is_hot",
        "meal_type",
        "tour_operator",
        "departure_city",
        "price_currency",
        "hotel__country",
    )
    search_fields = ("hotel__name", "hotel__resort", "external_id")
    date_hierarchy = "departure_date"
    autocomplete_fields = ("hotel", "tour_operator", "departure_city")
    readonly_fields = ("created_by", "created_at", "updated_at")
    list_select_related = ("hotel", "hotel__country", "tour_operator", "departure_city")
    ordering = ("-is_hot", "departure_date")
    list_per_page = 30
    actions = ("mark_as_hot", "unmark_as_hot", "mark_sold_out", "mark_active")

    fieldsets = (
        ("Тур", {
            "fields": (
                "hotel", "tour_operator", "departure_city",
                "departure_date", "nights",
                "adults_count", "children_count", "meal_type",
            )
        }),
        ("Цена и статус", {
            "fields": ("price_amount", "price_currency", "is_hot", "status")
        }),
        ("Импорт", {
            "fields": ("source", "external_id"),
            "classes": ("collapse",),
        }),
        ("Служебное", {
            "fields": ("created_by", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Отель", ordering="hotel__name")
    def hotel_link(self, obj):
        return format_html(
            "{} <span style='color:#888;'>({})</span>", obj.hotel.name, obj.hotel.country
        )

    @admin.display(description="Цена", ordering="price_amount")
    def price_display(self, obj):
        return format_html("<b>{}</b> {}", obj.price_amount, obj.get_price_currency_display())

    @admin.display(description="🔥", ordering="is_hot")
    def hot_badge(self, obj):
        return "🔥" if obj.is_hot else "—"

    @admin.display(description="Статус", ordering="status")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#000")
        return format_html(
            '<span style="padding:2px 8px;border-radius:10px;background:{};color:#fff;font-size:11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="🔥 Отметить как горящий")
    def mark_as_hot(self, request, queryset):
        updated = queryset.update(is_hot=True)
        self.message_user(request, f"Отмечено горящими: {updated}")

    @admin.action(description="Снять отметку 🔥")
    def unmark_as_hot(self, request, queryset):
        updated = queryset.update(is_hot=False)
        self.message_user(request, f"Снята отметка: {updated}")

    @admin.action(description="Отметить «Мест нет»")
    def mark_sold_out(self, request, queryset):
        updated = queryset.update(status=Tour.Status.SOLD_OUT)
        self.message_user(request, f"Обновлено: {updated}")

    @admin.action(description="Активировать")
    def mark_active(self, request, queryset):
        updated = queryset.update(status=Tour.Status.ACTIVE)
        self.message_user(request, f"Активировано: {updated}")


# ---------------------------------------------------------------------------
# Заявки
# ---------------------------------------------------------------------------

BOOKING_STATUS_COLORS = {
    BookingRequest.Status.NEW: "#1e88e5",
    BookingRequest.Status.IN_PROGRESS: "#fb8c00",
    BookingRequest.Status.CONFIRMED: "#43a047",
    BookingRequest.Status.CANCELLED: "#e53935",
}


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "tour", "status_badge", "manager", "created_at")
    list_filter = ("status", "manager")
    search_fields = ("full_name", "phone", "email", "tour__hotel__name")
    autocomplete_fields = ("tour", "manager")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    list_per_page = 25
    actions = ("mark_in_progress", "mark_confirmed", "mark_cancelled")

    fieldsets = (
        ("Клиент", {"fields": ("full_name", "phone", "email", "comment")}),
        ("Тур", {"fields": ("tour",)}),
        ("Обработка заявки", {"fields": ("status", "manager")}),
        ("Служебное", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Статус", ordering="status")
    def status_badge(self, obj):
        color = BOOKING_STATUS_COLORS.get(obj.status, "#000")
        return format_html(
            '<span style="padding:2px 8px;border-radius:10px;background:{};color:#fff;font-size:11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.action(description="Взять в работу")
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status=BookingRequest.Status.IN_PROGRESS)
        self.message_user(request, f"Обновлено: {updated}")

    @admin.action(description="Подтвердить")
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status=BookingRequest.Status.CONFIRMED)
        self.message_user(request, f"Подтверждено: {updated}")

    @admin.action(description="Отменить")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status=BookingRequest.Status.CANCELLED)
        self.message_user(request, f"Отменено: {updated}")


# ---------------------------------------------------------------------------
# Отзывы
# ---------------------------------------------------------------------------

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author_name", "tour", "stars_display", "is_published", "created_at")
    list_filter = ("is_published", "rating")
    search_fields = ("author_name", "text", "tour__hotel__name")
    autocomplete_fields = ("tour",)
    readonly_fields = ("created_at",)
    list_per_page = 25
    actions = ("publish_reviews", "unpublish_reviews")

    @admin.display(description="Оценка", ordering="rating")
    def stars_display(self, obj):
        return format_html(
            '<span style="color:#f5a623;">{}</span><span style="color:#ccc;">{}</span>',
            "★" * obj.rating,
            "★" * (5 - obj.rating),
        )

    @admin.action(description="Опубликовать")
    def publish_reviews(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Опубликовано: {updated}")

    @admin.action(description="Снять с публикации")
    def unpublish_reviews(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Снято: {updated}")
