# Generated by Django 2.1.5 on 2019-02-15 07:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('au_epa_data', '0005_auto_20190215_0635'),
    ]

    operations = [
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_start', models.DateTimeField(verbose_name='Date Time Start')),
                ('date_time_recorded', models.DateTimeField(verbose_name='Date Time Recorded')),
                ('value', models.CharField(blank=True, max_length=31, null=True, verbose_name='Value')),
                ('quality_status', models.PositiveSmallIntegerField(default=9, verbose_name='Quality Status')),
                ('aqi_index', models.PositiveSmallIntegerField(default=0, verbose_name='AQI Index')),
                ('aqi_category_threshold', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='common.AQICategoryThreshold', verbose_name='AQI Category')),
                ('equipment_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='au_epa_data.EquipmentType', verbose_name='Equipment Type')),
                ('health_category_threshold', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='common.HealthCategoryThreshold', verbose_name='Health Category')),
                ('monitor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='au_epa_data.Monitor', verbose_name='Monitor')),
                ('monitor_time_basis', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='au_epa_data.MonitorTimeBasis', verbose_name='Monitor Time Basis')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='au_epa_data.Site', verbose_name='Site')),
                ('time_basis', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='au_epa_data.TimeBasis', verbose_name='Time Basis')),
            ],
            options={
                'verbose_name': 'Measurement',
                'verbose_name_plural': 'Measurements',
                'db_table': 'measurement',
            },
        ),
        migrations.AlterUniqueTogether(
            name='measurement',
            unique_together={('date_time_start', 'site', 'monitor', 'time_basis')},
        ),
    ]
