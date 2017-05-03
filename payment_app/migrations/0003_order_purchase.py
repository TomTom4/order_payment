# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-28 12:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment_app', '0002_auto_20170427_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_identifier', models.CharField(max_length=55)),
                ('total_price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribut_dict', models.TextField(blank=True)),
                ('order_identifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='payment_app.Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase', to='payment_app.Product')),
                ('purchaser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
