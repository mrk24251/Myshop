# Generated by Django 3.0.4 on 2020-08-06 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_auto_20200806_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='HotDeal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='HotDealAmount',
            field=models.IntegerField(default=0),
        ),
    ]
