# Generated by Django 2.1.2 on 2018-11-27 16:01
# Updates all slugs for activities

from django.db import migrations
from django.utils.text import slugify


def forwards(apps, *args):
    Activity = apps.get_model("phmi", "Activity")
    activities = Activity.objects.filter(slug=None)
    for activity in activities:
        activity.slug = slugify(activity.name[:50])
        activity.save()


def backwards(*args):
    pass


class Migration(migrations.Migration):

    dependencies = [("phmi", "0015_activity_slug")]

    operations = [migrations.RunPython(forwards, backwards)]
