# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-04 13:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_auto_20160729_1531'),
        ('registration', '0003_auto_20161104_0936'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrants',
            name='crm_contact',
        ),
        migrations.AddField(
            model_name='registrants',
            name='crm_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.Person'),
        ),
    ]
