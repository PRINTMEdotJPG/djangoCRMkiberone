from django.contrib import admin
from django.utils.html import format_html  # Для безопасного HTML в админке
from django.urls import reverse  # Для построения URL в админке
from django.db.models import Count, Sum  # Для агрегации (подсчёта) данных
from .models import Parent, Child, Group, GroupType, Payment, TrialRequest

@admin.register(Parent)  # Декоратор для регистрации модели в админке
class ParentAdmin(admin.ModelAdmin):
    # list_display определяет, какие поля будут отображаться в списке записей
    # Каждое значение - это либо имя поля модели, либо метод этого класса
    list_display = (
        'full_name',      # поле из модели
        'phone_number',   # поле из модели
        'email',         # поле из модели
        'district',      # поле из модели
        'children_count', # метод, который мы определим ниже
        'total_payments', # метод, который мы определим ниже
        'is_active',     # поле из модели
        'created_at'     # поле из модели
    )

    # list_filter добавляет фильтры справа от списка
    # Пользователь сможет фильтровать записи по этим полям
    list_filter = ('is_active', 'district', 'created_at')

    # search_fields определяет, по каким полям можно производить поиск
    # Поиск будет работать по любому из указанных полей
    search_fields = ('full_name', 'phone_number', 'email')

    # Поля, которые нельзя редактировать
    readonly_fields = ('created_at', 'total_payments')

    # Действия, которые можно применить к выбранным записям
    actions = ['archive_parents', 'activate_parents']

    # fieldsets группирует поля в разделы при редактировании записи
    fieldsets = (
        ('Основная информация', {  # Название раздела
            'fields': ('full_name', 'phone_number', 'email')  # Поля в разделе
        }),
        ('Адрес', {
            'fields': ('location', 'district')
        }),
        ('Статус', {
            'fields': ('is_active', 'created_at')
        }),
        ('Финансы', {
            'fields': ('total_payments',)
        })
    )

    # Вложенные классы для отображения связанных моделей
    class ChildInline(admin.TabularInline):
        model = Child  # Связанная модель
        extra = 1     # Количество пустых форм для добавления
        show_change_link = True  # Добавляет ссылку на редактирование записи

    class PaymentInline(admin.TabularInline):
        model = Payment
        extra = 0  # Не показывать пустые формы
        can_delete = False  # Запретить удаление через инлайн
        readonly_fields = ('payment_date',)

    # Подключаем инлайны к родительской модели
    inlines = [ChildInline, PaymentInline]

    # Метод для подсчёта количества детей
    def children_count(self, obj):
        """
        obj - это экземпляр модели Parent
        Метод возвращает количество связанных детей
        """
        return obj.children.count()  # children - это related_name в модели Child
    children_count.short_description = 'Кол-во детей'  # Название столбца в админке

    # Метод для подсчёта суммы платежей
    def total_payments(self, obj):
        """
        Подсчитывает общую сумму платежей родителя
        aggregate() - метод для агрегации данных
        Sum() - суммирует значения поля 'amount'
        """
        total = obj.payments.aggregate(Sum('amount'))['amount__sum']
        return f"{total or 0} ₽"  # Если нет платежей, вернёт "0 ₽"
    total_payments.short_description = 'Сумма платежей'

    # Метод-действие для архивации родителей
    def archive_parents(self, request, queryset):
        """
        request - объект запроса
        queryset - набор выбранных записей
        """
        queryset.update(is_active=False)  # Обновляем все выбранные записи
        self.message_user(request, f"Выбранные родители перемещены в архив")
    archive_parents.short_description = "Переместить в архив"  # Название действия

    # Метод-действие для активации родителей
    def activate_parents(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Выбранные родители активированы")
    activate_parents.short_description = "Активировать"

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'groups_list')
    list_filter = ('age', 'groups')
    search_fields = ('full_name', 'parent__full_name')

    # Поля с автодополнением (select2 виджет)
    autocomplete_fields = ['parent']

    # def parent_link(self, obj):
    #     """
    #     Создаёт кликабельную ссылку на родителя
    #     reverse() генерирует URL для редактирования родителя
    #     format_html() безопасно вставляет HTML в админку
    #     """
    #     url = reverse('admin:myapp_parent_change', args=[obj.parent.id])
    #     return format_html('<a href="{}">{}</a>', url, obj.parent.full_name)
    # parent_link.short_description = 'Родитель'

    def groups_list(self, obj):
        """
        Возвращает список групп, в которых состоит ребёнок
        """
        return ", ".join([group.name for group in obj.groups.all()])
    groups_list.short_description = 'Группы'

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'group_type',
        'day_of_week',
        'time_start',
        'time_end',
        'students_count'
    )

    list_filter = ('group_type', 'day_of_week')
    search_fields = ('id',)
    filter_horizontal = ('students',)

    def students_count(self, obj):
        return obj.students.count()
    students_count.short_description = 'Количество учеников'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('parent', 'amount', 'payment_type', 'payment_date')
    list_filter = ('payment_type', 'payment_date')
    search_fields = ('parent__full_name',)  # Поиск по имени родителя
    readonly_fields = ('payment_date',)

    # date_hierarchy добавляет навигацию по датам сверху списка
    date_hierarchy = 'payment_date'

    def has_delete_permission(self, request, obj=None):
        """
        Запрещает удаление платежей через админку
        Это важно для сохранения истории платежей
        """
        return False

@admin.register(TrialRequest)
class TrialRequestAdmin(admin.ModelAdmin):
    list_display = (
        'parent_name',
        'phone_number',
        'child_name',
        'child_age',
        'status',
        'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('parent_name', 'phone_number', 'child_name')
    readonly_fields = ('created_at',)

    # Действия для массового изменения статуса заявок
    actions = ['mark_as_processed', 'mark_as_completed']

    def mark_as_processed(self, request, queryset):
        """
        Действие для изменения статуса выбранных заявок на 'В обработке'
        request - объект запроса
        queryset - выбранные записи
        """
        queryset.update(status='processed')
    mark_as_processed.short_description = "Отметить как 'В обработке'"

    def mark_as_completed(self, request, queryset):
        """
        Действие для изменения статуса выбранных заявок на 'Завершено'
        """
        queryset.update(status='completed')
    mark_as_completed.short_description = "Отметить как 'Завершено'"

# Дополнительные настройки внешнего вида админ-панели
admin.site.site_header = "CRM Школы программирования"  # Заголовок сайта
admin.site.site_title = "CRM Школы программирования"   # Заголовок вкладки
admin.site.index_title = "Управление школой"           # Заголовок главной страницы

"""
Примеры использования админки:

1. Работа с родителями:
   - Просмотр списка всех родителей
   - Фильтрация по району или статусу
   - Поиск по имени или телефону
   - Просмотр детей родителя и их групп
   - Просмотр платежей родителя
   - Архивация неактивных родителей

2. Работа с группами:
   - Создание новых групп
   - Добавление/удаление учеников из группы
   - Просмотр состава группы
   - Фильтрация по дням недели

3. Работа с платежами:
   - Добавление новых платежей
   - Просмотр истории платежей
   - Фильтрация по датам
   - Поиск платежей конкретного родителя

4. Работа с пробными заявками:
   - Обработка новых заявок
   - Изменение статуса заявок
   - Фильтрация по статусу
   - Поиск по контактным данным
"""

