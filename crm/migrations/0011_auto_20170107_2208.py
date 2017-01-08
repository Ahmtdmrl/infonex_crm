# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-08 03:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0010_person_linkedin'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('SA', 'Sales'), ('SP', 'Sponsorship'), ('PD', 'Conference Developer')], default='SA', max_length=2)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TerritorySelects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('include_exclude', models.CharField(choices=[('include', 'include'), ('exclude', 'exclude')], default='include', max_length=7)),
                ('geo', models.CharField(blank=True, choices=[('East', 'East'), ('West', 'West'), ('Maritimes/East', 'Maritimes'), ('USA', 'USA'), ('Other', 'Other Foreign'), ('Unknown', 'Unknown'), ('', '---')], default='', max_length=10)),
                ('main_category', models.CharField(blank=True, choices=[('HR', 'HR'), ('FIN', 'FIN'), ('Industry', 'Industry'), ('Aboriginal', 'Aboriginal'), ('Gov', 'Gov'), ('NA', 'None'), ('', '---')], default='', max_length=25)),
                ('main_category2', models.CharField(blank=True, choices=[('HR', 'HR'), ('FIN', 'FIN'), ('Industry', 'Industry'), ('Aboriginal', 'Aboriginal'), ('Gov', 'Gov'), ('NA', 'None'), ('', '---')], default='', max_length=15)),
                ('division1', models.CharField(blank=True, choices=[('1', '1 - Misc'), ('2', '2 - Misc'), ('3', '3 - Misc'), ('4', '4 - Misc'), ('5', '5 - Misc'), ('6', '6 - Misc'), ('A1', '1 - Accounting'), ('A2', '2 - Accounting'), ('A3', '3 - Accounting'), ('Aboriginal', 'Aboriginal'), ('FED 1', 'FED 1'), ('FED 2', 'FED 2'), ('FED 3', 'FED 3'), ('FED 4', 'FED 4'), ('USA', 'USA'), ('NA', 'Not Determined'), ('', '---')], default='', max_length=20)),
                ('division2', models.CharField(blank=True, choices=[('1', '1 - Misc'), ('2', '2 - Misc'), ('3', '3 - Misc'), ('4', '4 - Misc'), ('5', '5 - Misc'), ('6', '6 - Misc'), ('A1', '1 - Accounting'), ('A2', '2 - Accounting'), ('A3', '3 - Accounting'), ('Aboriginal', 'Aboriginal'), ('FED 1', 'FED 1'), ('FED 2', 'FED 2'), ('FED 3', 'FED 3'), ('FED 4', 'FED 4'), ('USA', 'USA'), ('NA', 'Not Determined'), ('', '---')], default='', max_length=20)),
                ('company', models.CharField(blank=True, max_length=100)),
                ('industry', models.CharField(blank=True, max_length=100)),
                ('event_assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.EventAssignment')),
            ],
        ),
        migrations.AlterField(
            model_name='person',
            name='dept',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='territoryselects',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.Person'),
        ),
    ]
