# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-03 22:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0009_eventoptions_primary'),
    ]

    operations = [
        migrations.RenameField(
            model_name='regdetails',
            old_name='depost_method',
            new_name='deposit_method',
        ),
    ]
