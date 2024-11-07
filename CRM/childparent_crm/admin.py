from django.contrib import admin, messages
from django.urls import path
from django.utils.html import format_html  # Для безопасного HTML в админке
from django.urls import reverse  # Для построения URL в админке
from django.db.models import Count, Sum  # Для агрегации (подсчёта) данных
from .models import Parent, Child, Group, GroupType, Payment, TrialRequest, ParentComment, MakeupClass, Absence
from .forms import ParentCommentInlineForm
from django.shortcuts import render, redirect
from datetime import datetime




class ParentCommentInline(admin.StackedInline):
    model = ParentComment
    form = ParentCommentInlineForm
    extra = 1
    fields = ('text',)

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

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
        'subscription_amount',
        'total_payments', # метод, который мы определим ниже
        'is_active',     # поле из модели
        'created_at',     # поле из модели
        'last_comment' # кастомный метод, позволяющий отображать комментарии менеджеров
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
            'fields': ('location', 'district', 'subscription_amount')
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
        extra = 0     # Количество пустых форм для добавления
        show_change_link = True  # Добавляет ссылку на редактирование записи

    class PaymentInline(admin.TabularInline):
        model = Payment
        extra = 1 # Не показывать пустые формы
        can_delete = False  # Запретить удаление через инлайн
        readonly_fields = ('payment_date',)

    # Подключаем инлайны к родительской модели
    inlines = [ChildInline, PaymentInline, ParentCommentInline]

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

    # Отображение комментария
    def last_comment(self, obj):
        latest_comment = obj.comments.first()
        if latest_comment:
            return f'{latest_comment.text[:50]}... ({latest_comment.created_by}, {latest_comment.created_at.strftime("%d.%m.%Y")})'
        return '-'

    last_comment.short_description = 'Последний комментарий'

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ParentComment) and not instance.created_by:
                instance.created_by = request.user
            instance.save()
        formset.save_m2m()

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'birth_date', 'location', 'get_district', 'get_parent_link', 'groups_list')
    list_filter = ('age', 'birth_date', 'parent__district', )
    search_fields = ('full_name', 'birth_date',)

    readonly_fields = ('age', 'location', 'get_district', )


    def location(self, obj):
        return obj.parent.location
    location.short_description = 'Локация'

    def get_district(self, obj):
        return obj.parent.district if obj.parent else None
    get_district.short_description = 'Район'

    def get_queryset(self, request):
        # Используем только 'parent', если district это поле в модели Parent
        return super().get_queryset(request).select_related('parent')

    def get_parent_link(self, obj):
        if obj.parent:
            url = reverse('admin:childparent_crm_parent_change', args=[obj.parent.id])
            return format_html('<a href="{}">{}</a>', url, obj.parent.full_name)
        return "-"
    get_parent_link.short_description = 'Родитель'

    def groups_list(self, obj):
        """
        Возвращает список групп, в которых состоит ребёнок
        """
        return ", ".join([f"{group.group_type} {group.day_of_week} в {group.time_start}" for group in obj.groups.all()])
    groups_list.short_description = 'Группы'

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'group_type',
        'day_of_week',
        'time_start',
        'time_end',
        'students_count',
        'mark_absences',
    )

    list_filter = ('group_type', 'day_of_week')
    search_fields = ('id',)
    filter_horizontal = ('students',)

    def students_count(self, obj):
        return obj.students.count()
    students_count.short_description = 'Количество учеников'

    def mark_absences(self, obj):
        """Кнопка для отметки пропусков"""
        url = reverse('admin:mark-group-absences', args=[obj.pk])
        return format_html('<a class="button" href="{}">Отметить пропуски</a>', url)

    mark_absences.short_description = 'Отметить пропуски'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:group_id>/mark-absences/',
                self.admin_site.admin_view(self.mark_absences_view),
                name='mark-group-absences'
            ),
        ]
        return custom_urls + urls

    def mark_absences_view(self, request, group_id):
        group = Group.objects.get(id=group_id)
        students = group.students.all()

        if request.method == 'POST':
            date = request.POST.get('date')
            absent_students = request.POST.getlist('absent_students')

            for student_id in absent_students:
                student = Child.objects.get(id=student_id)
                if not Absence.objects.filter(child=student, date=date).exists():
                    Absence.objects.create(
                        child=student,
                        date=date,
                        status='missed'
                    )

            messages.success(request, f'Пропуски для группы {group.id} успешно отмечены')
            return redirect('..')

        context = {
            'title': f'Отметить пропуски - Группа {group.id} ({group.group_type})',
            'group': group,
            'students': students,
            'opts': self.model._meta,
            'today': datetime.now().date(),
        }
        return render(request, 'admin/mark_absences.html', context)

@admin.register(MakeupClass)
class MakeupClassAdmin(admin.ModelAdmin):
    # Отображаемые поля в списке
    list_display = ['get_child_name', 'makeup_date', 'time_slot', 'status', 'group', 'reason', 'slot_capacity']

    # Фильтры справа
    list_filter = ['status', 'makeup_date', 'group']

    # Поля для поиска
    search_fields = ['absence__child__full_name']

    # Поля только для чтения
    readonly_fields = ['created_at', 'updated_at']

    def get_child_name(self, obj):
        """Получение имени ученика"""
        return obj.absence.child.full_name
    get_child_name.short_description = 'Ученик'

    def slot_capacity(self, obj):
        """Отображение заполненности слота"""
        total = MakeupClass.objects.filter(
            makeup_date=obj.makeup_date,
            time_slot=obj.time_slot,
            status='scheduled'  # Считаем только запланированные
        ).count()

        # Определяем цвет индикатора
        if total >= 4:
            color = 'red'
        elif total >= 2:
            color = 'orange'
        else:
            color = 'green'

        return format_html(
            '<span style="color: {};">{}/4</span>',
            color,
            total
        )
    slot_capacity.short_description = 'Заполненность слота'

    def save_model(self, request, obj, form, change):
        """Обработка сохранения модели"""
        # Проверяем количество учеников в слоте
        total_in_slot = MakeupClass.objects.filter(
            makeup_date=obj.makeup_date,
            time_slot=obj.time_slot,
            status='scheduled'
        ).count()

        # Если это новая запись и слот заполнен
        if not change and total_in_slot >= 4:
            messages.error(request, 'Этот слот уже заполнен (максимум 4 ученика)')
            return

        super().save_model(request, obj, form, change)

        # Обновляем статус пропуска
        absence = obj.absence
        if obj.status == 'completed':
            absence.status = 'completed'
        elif obj.status == 'scheduled':
            absence.status = 'scheduled'
        absence.save()

@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ['child', 'date', 'status', 'get_makeup_info', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['child__full_name']
    readonly_fields = ['created_at']
    actions = ['mark_as_completed']

    def get_makeup_info(self, obj):
        """Получение информации об отработке"""
        try:
            makeup = MakeupClass.objects.get(absence=obj)
            status_colors = {
                'scheduled': 'blue',
                'completed': 'green',
                'cancelled': 'red'
            }
            return format_html(
                '<span style="color: {};">Отработка: {} в {} ({})</span>',
                status_colors.get(makeup.status, 'black'),
                makeup.makeup_date,
                makeup.time_slot,
                makeup.get_status_display()
            )
        except MakeupClass.DoesNotExist:
            return format_html(
                '<span style="color: grey;">Не назначена</span>'
            )
    get_makeup_info.short_description = 'Информация об отработке'

    def mark_as_completed(self, request, queryset):
        """Массовая отметка отработок как выполненных"""
        updated = 0
        for absence in queryset:
            try:
                makeup = MakeupClass.objects.get(absence=absence)
                if makeup.status == 'scheduled':
                    makeup.status = 'completed'
                    makeup.save()
                    absence.status = 'completed'
                    absence.save()
                    updated += 1
            except MakeupClass.DoesNotExist:
                continue

        if updated:
            self.message_user(
                request,
                f'Успешно отмечено выполненными: {updated} отработок'
            )
        else:
            self.message_user(
                request,
                'Не найдено запланированных отработок для отметки',
                level=messages.WARNING
            )
    mark_as_completed.short_description = 'Отметить как выполненные'

    def save_model(self, request, obj, form, change):
        """Обработка сохранения пропуска"""
        # Если статус меняется на completed
        if 'status' in form.changed_data and obj.status == 'completed':
            try:
                makeup = MakeupClass.objects.get(absence=obj)
                makeup.status = 'completed'
                makeup.save()
            except MakeupClass.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        """Запрет удаления пропусков с назначенными отработками"""
        if obj:
            try:
                MakeupClass.objects.get(absence=obj)
                return False
            except MakeupClass.DoesNotExist:
                pass
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """Делаем поля только для чтения если есть отработка"""
        if obj:
            try:
                MakeupClass.objects.get(absence=obj)
                return self.readonly_fields + ['status']
            except MakeupClass.DoesNotExist:
                pass
        return self.readonly_fields


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

