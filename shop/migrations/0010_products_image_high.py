# Generated by Django 3.0.8 on 2020-07-15 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_auto_20200712_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='image_high',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]