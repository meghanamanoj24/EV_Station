# Generated by Django 3.2.5 on 2023-10-24 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0002_service_reg'),
    ]

    operations = [
        migrations.CreateModel(
            name='feed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=20)),
                ('message', models.IntegerField()),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
