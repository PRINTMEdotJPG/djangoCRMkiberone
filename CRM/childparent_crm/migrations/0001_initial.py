# Generated by Django 5.1.2 on 2024-11-02 21:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100, verbose_name='ФИО')),
                ('age', models.IntegerField(verbose_name='Возраст')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Ребенок',
                'verbose_name_plural': 'Дети',
            },
        ),
        migrations.CreateModel(
            name='GroupType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'verbose_name': 'Тип группы',
                'verbose_name_plural': 'Типы групп',
            },
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100, verbose_name='ФИО')),
                ('phone_number', models.CharField(max_length=15, verbose_name='Телефон')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('location', models.CharField(max_length=100, verbose_name='Город')),
                ('district', models.CharField(max_length=100, verbose_name='Район')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активный клиент')),
            ],
            options={
                'verbose_name': 'Родитель',
                'verbose_name_plural': 'Родители',
            },
        ),
        migrations.CreateModel(
            name='TrialRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_name', models.CharField(max_length=100, verbose_name='ФИО родителя')),
                ('phone_number', models.CharField(max_length=15, verbose_name='Телефон')),
                ('child_name', models.CharField(max_length=100, verbose_name='ФИО ребенка')),
                ('child_age', models.IntegerField(verbose_name='Возраст ребенка')),
                ('preferred_time', models.CharField(max_length=100, verbose_name='Предпочитаемое время')),
                ('status', models.CharField(choices=[('new', 'Новая'), ('processed', 'В обработке'), ('confirmed', 'Подтверждена'), ('completed', 'Завершена'), ('cancelled', 'Отменена')], default='new', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Заявка на пробное',
                'verbose_name_plural': 'Заявки на пробное',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(max_length=20, verbose_name='День недели')),
                ('time_start', models.TimeField(verbose_name='Время начала')),
                ('time_end', models.TimeField(verbose_name='Время окончания')),
                ('students', models.ManyToManyField(blank=True, related_name='groups', to='childparent_crm.child')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='childparent_crm.grouptype')),
            ],
            options={
                'verbose_name': 'Группа',
                'verbose_name_plural': 'Группы',
            },
        ),
        migrations.AddField(
            model_name='child',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='childparent_crm.parent'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('payment_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата платежа')),
                ('payment_type', models.CharField(choices=[('cash', 'Наличные'), ('card', 'Карта'), ('transfer', 'Перевод')], max_length=50, verbose_name='Тип оплаты')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='childparent_crm.parent')),
            ],
            options={
                'verbose_name': 'Платеж',
                'verbose_name_plural': 'Платежи',
            },
        ),
    ]