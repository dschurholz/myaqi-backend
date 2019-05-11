# Generated by Django 2.1.5 on 2019-05-07 04:20

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firetype', models.CharField(max_length=8, verbose_name='Fire Type')),
                ('season', models.IntegerField(verbose_name='Season')),
                ('fire_no', models.CharField(max_length=25, verbose_name='Fire Number')),
                ('name', models.CharField(max_length=254, verbose_name='Name')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Start Date')),
                ('strtdatit', models.BigIntegerField(verbose_name='Start Date (Int)')),
                ('treat_type', models.CharField(max_length=50, verbose_name='Treatment Type')),
                ('fire_svrty', models.CharField(max_length=25, verbose_name='Fire Severity')),
                ('fire_cover', models.CharField(max_length=50, verbose_name='Fire Cover')),
                ('firekey', models.CharField(max_length=50, verbose_name='Fire Key')),
                ('cr_date', models.DateField(blank=True, null=True, verbose_name='Creation Date')),
                ('updatedate', models.DateField(blank=True, null=True, verbose_name='Update Date')),
                ('area_ha', models.FloatField(verbose_name='Area (Hectares)')),
                ('method', models.CharField(max_length=50, verbose_name='Method')),
                ('methd_cmnt', models.CharField(max_length=254, verbose_name='Method Comment')),
                ('accuracy', models.CharField(max_length=50, verbose_name='Accuracy')),
                ('dse_id', models.BigIntegerField(verbose_name='DSE Id')),
                ('cfa_id', models.BigIntegerField(verbose_name='CFA Id')),
                ('districtid', models.CharField(max_length=2, verbose_name='District Id')),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, verbose_name='Geometry')),
            ],
            options={
                'verbose_name': 'Fire',
                'verbose_name_plural': 'Fires',
                'db_table': 'fire',
                'ordering': ('-season', '-start_date', 'name'),
            },
        ),
    ]
