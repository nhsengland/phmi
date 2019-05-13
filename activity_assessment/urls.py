from django.urls import path

from .views import ActivityAssessmentView, ActivityResultView

urlpatterns = [
    path("activity_assessment/", ActivityAssessmentView.as_view(), name="activity-assessment"),
    path(
        "activity_assessment/<str:activity_sign>",
        ActivityResultView.as_view(),
        name="activity-assessment-result",
    ),
]
