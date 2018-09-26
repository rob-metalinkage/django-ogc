# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-09-22 04:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('skosxl', '0012_auto_20180705_1559'),
    ]

    operations = [
        migrations.CreateModel(
            name='GMLDict',
            fields=[
                ('importedconceptscheme_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='skosxl.ImportedConceptScheme')),
            ],
            bases=('skosxl.importedconceptscheme',),
        ),
    ]
