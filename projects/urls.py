from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from projects import views

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path(
        "projects/",
        views.ProjectLocationView.as_view(),
        name="project-location"
    ),
    path(
        "projects/<str:location_sign>",
        views.ProjectActivityView.as_view(),
        name="project-activity"
    ),
    path(
        "projects/<str:location_sign>/<str:activity_sign>",
        views.ProjectResultView.as_view(),
        name="project-result"
    ),
]