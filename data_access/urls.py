from django.urls import path

from .views import (
    ActivitiesView,
    ActivityCategoryView,
    OrgTypesView,
    OutcomeView,
    ServicesView,
)

urlpatterns = [
    path("/", ActivityCategoryView.as_view(), name="categories"),
    path("activities/<str:signed_data>", ActivitiesView.as_view(), name="activities"),
    path("org-types/<str:signed_data>", OrgTypesView.as_view(), name="org-types"),
    path("services/<str:signed_data>", ServicesView.as_view(), name="services"),
    path("outcome/<str:signed_data>", OutcomeView.as_view(), name="outcome"),
]
