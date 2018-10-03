# Generated by Django 2.1.2 on 2018-10-04 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CareSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='GroupType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('ods_code', models.TextField(unique=True)),
                ('care_system', models.ManyToManyField(related_name='orgs', to='phmi.CareSystem')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='OrgType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='organisation',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orgs', to='phmi.OrgType'),
        ),
        migrations.AddField(
            model_name='caresystem',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='care_systems', to='phmi.GroupType'),
        ),
        migrations.AlterUniqueTogether(
            name='caresystem',
            unique_together={('type', 'name')},
        ),
    ]
