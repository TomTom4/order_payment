# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-01 13:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0006_auto_20170428_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='name',
            field=models.CharField(default='toto_product', max_length=55),
            preserve_default=False,
        ),
    ]
