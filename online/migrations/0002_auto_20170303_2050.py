# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-03-03 20:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('online', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Online',
            new_name='Cities',
        ),
    ]
