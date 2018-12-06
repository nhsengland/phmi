# Generated by Django 2.1.3 on 2018-12-05 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phmi', '0022_auto_20181205_1145'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statute',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='legaljustification',
            name='statutes',
            field=models.ManyToManyField(blank=True, to='phmi.Statute'),
        ),
        migrations.AlterField(
            model_name='statute',
            name='link',
            field=models.URLField(unique=True),
        ),
    ]
