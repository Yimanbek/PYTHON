# Generated by Django 5.0.1 on 2024-01-12 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_customuser_managers_alter_customuser_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='password_change_code',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]