# Generated by Django 5.1.2 on 2024-11-03 19:45

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('childparent_crm', '0002_remove_group_type_group_group_type_alter_group_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='time_end',
            field=models.TimeField(blank=True, verbose_name='Время окончания'),
        ),
        migrations.CreateModel(
            name='ParentComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Менеджер')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='childparent_crm.parent')),
            ],
            options={
                'verbose_name': 'Комментарий к родителю',
                'verbose_name_plural': 'Комментарии к родителям',
                'ordering': ['-created_at'],
            },
        ),
    ]