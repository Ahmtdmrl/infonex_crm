# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-02 21:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_auto_20161129_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='linkedin',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]