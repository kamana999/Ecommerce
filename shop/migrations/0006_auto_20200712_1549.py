# Generated by Django 3.0.8 on 2020-07-12 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_auto_20200712_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address_type',
            field=models.CharField(choices=[('H', 'HOME'), ('W', 'WORK')], max_length=2),
        ),
        migrations.AlterField(
            model_name='brandname',
            name='brand_logo',
            field=models.ImageField(upload_to='brand_logo'),
        ),
    ]
