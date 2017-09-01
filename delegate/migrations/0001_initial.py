# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-01 13:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm', '0032_auto_20170901_0944'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='QueuedOrders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('salutation', models.CharField(blank=True, max_length=15, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('email1', models.EmailField(blank=True, max_length=254, null=True)),
                ('email2', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone1', models.CharField(blank=True, max_length=25, null=True)),
                ('phone2', models.CharField(blank=True, max_length=25, null=True)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('address1', models.CharField(blank=True, max_length=255, null=True)),
                ('address2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state_prov', models.CharField(blank=True, choices=[('', 'Any'), ('AB', 'Alberta'), ('BC', 'British Columbia'), ('MB', 'Manitoba'), ('NB', 'New Brunswick'), ('NL', 'Newfoundland and Labrador'), ('NT', 'Northwest Territories'), ('NS', 'Nova Scotia'), ('NU', 'Nunavut'), ('ON', 'Ontario'), ('PEI', 'Prince Edward Island'), ('QC', 'Quebec'), ('SK', 'Saskatchewan'), ('YK', 'Yukon'), ('', '-----------'), ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], max_length=25, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=25, null=True)),
                ('country', models.CharField(blank=True, max_length=25, null=True)),
                ('registration_status', models.CharField(choices=[('', '-----------'), ('DU', 'Delegate Unpaid'), ('DP', 'Delegate Paid'), ('DF', 'Delegate Free'), ('K', 'Speaker'), ('SP', 'Sponsor Paid'), ('SU', 'Sponsor Unpaid'), ('SD', 'Sponsor Delegate'), ('SE', 'Sponsor Exhibitor'), ('G', 'Guest'), ('DX', 'Delegate cancelled - paid'), ('UX', 'Delegate cancelled - unpaid'), ('SX', 'Sponsor cancelled'), ('KX', 'Speaker cancelled'), ('B', 'Substituted Out')], default='DU', max_length=2)),
                ('registration_notes', models.TextField(blank=True, null=True)),
                ('pre_tax_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('gst_rate', models.DecimalField(blank=True, decimal_places=5, default=0.05, max_digits=6, null=True)),
                ('hst_rate', models.DecimalField(blank=True, decimal_places=5, default=0.13, max_digits=6, null=True)),
                ('qst_rate', models.DecimalField(blank=True, decimal_places=5, default=0.09975, max_digits=6, null=True)),
                ('payment_method', models.CharField(blank=True, choices=[('V', 'Visa'), ('M', 'MasterCard'), ('A', 'AMEX'), ('C', 'Cheque'), ('W', 'Wire Transfer'), ('N', 'Credit Note'), ('O', 'Other method')], max_length=1, null=True)),
                ('invoice_notes', models.TextField(blank=True, null=True)),
                ('asst_salutation', models.CharField(blank=True, max_length=15, null=True)),
                ('asst_first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('asst_last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('asst_title', models.CharField(blank=True, max_length=100, null=True)),
                ('asst_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('asst_phone', models.CharField(blank=True, max_length=25, null=True)),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Event')),
                ('sales_credit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
