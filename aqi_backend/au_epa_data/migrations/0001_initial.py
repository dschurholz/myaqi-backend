# Generated by Django 2.1.5 on 2019-02-14 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emv_url', models.URLField(blank=True, null=True, verbose_name='EMV Url')),
                ('incident_icon', models.URLField(blank=True, null=True, verbose_name='Incident Icon URL')),
            ],
            options={
                'verbose_name': 'Incident Site',
                'verbose_name_plural': 'Incident Sites',
                'db_table': 'incident_site',
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('site_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='Site ID')),
                ('name', models.CharField(blank=True, max_length=63, null=True, verbose_name='Name')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=16, null=True, verbose_name='Latitude')),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=16, null=True, verbose_name='Longitude')),
                ('fire_hazard_category', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Fire Hazard Category')),
                ('is_station_offline', models.BooleanField(default=False, verbose_name='Is Station Offline')),
                ('has_incident', models.BooleanField(default=False, verbose_name='Has Incident')),
                ('incident_type', models.CharField(blank=True, max_length=31, null=True, verbose_name='Incident Type')),
            ],
            options={
                'verbose_name': 'Site',
                'verbose_name_plural': 'Sites',
                'db_table': 'site',
            },
        ),
        migrations.CreateModel(
            name='SiteList',
            fields=[
                ('name', models.CharField(max_length=63, primary_key=True, serialize=False, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Site List',
                'verbose_name_plural': 'Site Lists',
                'db_table': 'site_list',
            },
        ),
        migrations.AddField(
            model_name='site',
            name='site_list',
            field=models.ManyToManyField(blank=True, to='au_epa_data.SiteList', verbose_name='Site List'),
        ),
        migrations.AddField(
            model_name='incidentsite',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incidents', to='au_epa_data.Site', verbose_name='Site'),
        ),
    ]
