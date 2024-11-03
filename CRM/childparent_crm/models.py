# models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class GroupType(models.Model):
    """Модель для типов групп (младшая/средняя/старшая)"""
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return "Группа: " + str(self.name)

    class Meta:
        verbose_name = 'Тип группы'
        verbose_name_plural = 'Типы групп'

class ParentComment(models.Model):
    parent = models.ForeignKey('Parent', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField('Комментарий')
    created_at = models.DateTimeField('Дата создания', default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Менеджер')

    class Meta:
        verbose_name = 'Комментарий к родителю'
        verbose_name_plural = 'Комментарии к родителям'
        ordering = ['-created_at']

    def __str__(self):
        return f'Менеджер {self.created_by} в {self.created_at.strftime("%d.%m.%Y %H:%M")}'


class Parent(models.Model):
    """Модель для хранения информации о родителях"""
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    phone_number = models.CharField(max_length=15, verbose_name='Телефон')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    location = models.CharField(max_length=100, verbose_name='Город')
    district = models.CharField(max_length=100, verbose_name='Район')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    # Если клиент ушёл по какой угодно причине, он становится "неактивным" (архивированным)
    is_active = models.BooleanField(default=True, verbose_name='Активный клиент')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Родитель'
        verbose_name_plural = 'Родители'

class Child(models.Model):
    """Модель для хранения информации о детях"""
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    age = models.IntegerField(verbose_name='Возраст')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ребенок: {self.full_name}, ФИО родителя: ({self.parent.full_name})"

    class Meta:
        verbose_name = 'Ребенок'
        verbose_name_plural = 'Дети'

# models.py

# models.py

class Group(models.Model):
    id = models.AutoField(primary_key=True)  # Используем стандартное поле id
    group_type = models.CharField(max_length=100, verbose_name='Тип группы', default="-")
    day_of_week = models.CharField(max_length=20, verbose_name='День недели')
    time_start = models.TimeField(verbose_name='Время начала')
    time_end = models.TimeField(verbose_name='Время окончания', blank=True)
    students = models.ManyToManyField('Child', blank=True, related_name='groups')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        db_table = 'childparent_crm_group'

    def save(self, *args, **kwargs):
        if self.time_start and not self.time_end:
            # Объединяем текущую дату с временем начала
            datetime_start = datetime.combine(datetime.today(), self.time_start)
            # Прибавляем 2 часа
            datetime_end = datetime_start + timedelta(hours=2)
            # Устанавливаем время окончания
            self.time_end = datetime_end.time()
        super(Group, self).save(*args, **kwargs)

    def __str__(self):
        return f"Группа {self.id} ({self.group_type})"

class Payment(models.Model):
    """Модель для платежей"""
    PAYMENT_TYPES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('transfer', 'Перевод'),
    ]

    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата платежа')
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPES, verbose_name='Тип оплаты')

    def __str__(self):
        return f"Платеж от {self.parent.full_name} на сумму {self.amount}"

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

class TrialRequest(models.Model):
    """Модель для заявок на пробные занятия"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('processed', 'В обработке'),
        ('confirmed', 'Подтверждена'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    parent_name = models.CharField(max_length=100, verbose_name='ФИО родителя')
    phone_number = models.CharField(max_length=15, verbose_name='Телефон')
    child_name = models.CharField(max_length=100, verbose_name='ФИО ребенка')
    child_age = models.IntegerField(verbose_name='Возраст ребенка')
    preferred_time = models.CharField(max_length=100, verbose_name='Предпочитаемое время')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заявка от {self.parent_name} ({self.status})"

    class Meta:
        verbose_name = 'Заявка на пробное'
        verbose_name_plural = 'Заявки на пробное'

