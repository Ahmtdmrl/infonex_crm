# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-24 16:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0017_auto_20170113_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag', models.CharField(blank=True, default='', max_length=1)),
                ('follow_up_date', models.DateField(blank=True, null=True)),
                ('event_assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.EventAssignment')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Person')),
            ],
        ),
        migrations.AlterField(
            model_name='personallistselections',
            name='include_exclude',
            field=models.CharField(choices=[('filter', "Filter (exclude values that don't match)"), ('add', 'Add to List'), ('exclude', 'Exclude from list')], default='filter', max_length=7),
        ),
        migrations.AlterUniqueTogether(
            name='flags',
            unique_together=set([('event_assignment', 'person')]),
        ),
    ]
