# Generated by Django 4.2.1 on 2023-05-12 03:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_remove_comment_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.template'),
        ),
    ]
