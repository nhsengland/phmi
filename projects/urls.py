from django.urls import path

from .views import ProjectActivityView, ProjectLocationView, ProjectResultView

urlpatterns = [

    path(
        "projects/",
        ProjectLocationView.as_view(),
        name="project-location"
    ),
    path(
        "projects/<str:location_sign>",
        ProjectActivityView.as_view(),
        name="project-activity"
    ),
    path(
        "projects/<str:location_sign>/<str:activity_sign>",
        ProjectResultView.as_view(),
        name="project-result"
    ),
]
