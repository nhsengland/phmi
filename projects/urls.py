from django.urls import path

from .views import ProjectActivityView, ProjectResultView

urlpatterns = [
    path("projects/", ProjectActivityView.as_view(), name="project-activity"),
    path(
        "projects/<str:activity_sign>",
        ProjectResultView.as_view(),
        name="project-result",
    ),
]
