# Generated by Django 3.0.4 on 2020-08-06 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_auto_20200806_1506'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='valid_to',
        ),
    ]