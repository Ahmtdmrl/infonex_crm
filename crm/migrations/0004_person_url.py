# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-09 21:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_reghistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]