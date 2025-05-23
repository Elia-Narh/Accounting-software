# Generated by Django 4.2.7 on 2025-02-23 09:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('school_app', '0002_chatmessage_alter_notification_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('event_type', models.CharField(choices=[('CONFERENCE', 'Parent-Teacher Conference'), ('MEETING', 'School Meeting'), ('ACTIVITY', 'School Activity'), ('HOLIDAY', 'School Holiday'), ('OTHER', 'Other Event')], max_length=20)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('location', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('color', models.CharField(default='#3788d8', max_length=7)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['start_date'],
            },
        ),
    ]
