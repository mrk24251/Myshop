# Generated by Django 3.1.1 on 2020-09-16 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_subscription', '0002_delete_emailcontacttranslation'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailcontact',
            name='email',
            field=models.EmailField(default=1, max_length=250),
            preserve_default=False,
        ),
    ]
