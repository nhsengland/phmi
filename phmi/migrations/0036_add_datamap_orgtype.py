# Generated by Django 2.1.5 on 2019-01-23 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("phmi", "0035_add_datamap_activities")]

    operations = [
        migrations.AddField(
            model_name="datatype",
            name="org_types",
            field=models.ManyToManyField(related_name="data_types", to="phmi.OrgType"),
        )
    ]
