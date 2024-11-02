from django.contrib import admin  # Импорт модуля админки Django
from .models import Parent, Child, Group, GroupType, Payment, TrialRequest  # Импорт моделей

@admin.register(Parent)  # Декоратор для регистрации модели в админке (альтернатива admin.site.register())
class ParentAdmin(admin.ModelAdmin):  # Класс для настройки отображения модели Parent в админке
    # Поля, которые будут отображаться в списке записей
    list_display = ('full_name', 'phone_number', 'email', 'district', 'is_active', 'created_at')

    # Фильтры, которые будут доступны справа в списке записей
    list_filter = ('is_active', 'district', 'created_at')

    # Поля, по которым можно производить поиск
    search_fields = ('full_name', 'phone_number', 'email')

    # Поля, которые нельзя редактировать
    readonly_fields = ('created_at',)

    # Вложенный класс для отображения связанных детей прямо в форме родителя
    class ChildInline(admin.TabularInline):
        model = Child  # Модель, которая будет отображаться
        extra = 1     # Количество пустых форм для добавления новых записей

    # Подключение вложенного отображения детей
    inlines = [ChildInline]

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'parent', 'get_groups')
    list_filter = ('age', 'groups')
    search_fields = ('full_name', 'parent__full_name')  # parent__full_name позволяет искать по имени родителя

    # Метод для получения списка групп ребенка
    def get_groups(self, obj):
        # Преобразование QuerySet групп в строку, разделенную запятыми
        return ", ".join([str(group) for group in obj.groups.all()])
    get_groups.short_description = 'Группы'  # Название колонки в админке

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('type', 'day_of_week', 'time_start', 'time_end', 'get_students_count')
    list_filter = ('type', 'day_of_week')

    # Специальный виджет для удобного выбора множества студентов (с двумя колонками и поиском)
    filter_horizontal = ('students',)

    # Метод для подсчета количества студентов в группе
    def get_students_count(self, obj):
        return obj.students.count()
    get_students_count.short_description = 'Количество учеников'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('parent', 'amount', 'payment_type', 'payment_date')
    list_filter = ('payment_type', 'payment_date')
    search_fields = ('parent__full_name',)

@admin.register(TrialRequest)
class TrialRequestAdmin(admin.ModelAdmin):
    list_display = ('parent_name', 'phone_number', 'child_name', 'child_age', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('parent_name', 'phone_number', 'child_name')
    readonly_fields = ('created_at',)

# Простая регистрация модели без дополнительных настроек
admin.site.register(GroupType)
