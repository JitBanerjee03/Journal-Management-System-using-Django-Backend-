# Generated by Django 5.2 on 2025-04-30 11:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0001_initial'),
        ('journal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='co_authors',
            field=models.ManyToManyField(blank=True, related_name='coauthored_journals', to='author.author'),
        ),
        migrations.AlterField(
            model_name='journal',
            name='corresponding_author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='author.author'),
        ),
    ]
