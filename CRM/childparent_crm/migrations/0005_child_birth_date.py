# Generated by Django 5.1.2 on 2024-11-06 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('childparent_crm', '0004_parent_subscription_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рождения: '),
        ),
    ]