# Generated by Django 2.1.5 on 2019-02-14 12:51

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AQIOrganization',
            fields=[
                ('abbreviation', models.CharField(max_length=5, primary_key=True, verbose_name='Abbrevation')),
                ('name', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Description')),
                ('logo', models.URLField(blank=True, null=True, verbose_name='Logo')),
            ],
            options={
                'verbose_name': 'AQI Organization',
                'verbose_name_plural': 'AQI Organizations',
                'db_table': 'aqi_organization',
            },
        )
    ]
