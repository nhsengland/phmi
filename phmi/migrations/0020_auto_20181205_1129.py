# Generated by Django 2.1.3 on 2018-12-05 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("phmi", "0019_auto_20181204_1710")]

    operations = [
        migrations.CreateModel(
            name="StatuteLink",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                ("link", models.URLField()),
            ],
        ),
        migrations.AlterModelOptions(
            name="organisation", options={"ordering": ["type__name", "name"]}
        ),
        migrations.AddField(
            model_name="legaljustification",
            name="statute_link",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="statutelink",
            name="justification",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="phmi.LegalJustification",
            ),
        ),
    ]
