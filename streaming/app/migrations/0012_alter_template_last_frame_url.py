# Generated by Django 4.2.1 on 2023-05-19 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_template_last_frame_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='last_frame_url',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
