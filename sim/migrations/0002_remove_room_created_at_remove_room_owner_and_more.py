# Generated by Django 5.1.5 on 2025-01-27 08:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='room',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='room',
            name='participants',
        ),
        migrations.AddField(
            model_name='room',
            name='players',
            field=models.ManyToManyField(blank=True, related_name='rooms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='room_id',
            field=models.CharField(default=1, max_length=10, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='word_selection',
            field=models.CharField(default='default', max_length=50),
        ),
        migrations.AlterField(
            model_name='room',
            name='difficulty',
            field=models.IntegerField(default=2),
        ),
    ]
