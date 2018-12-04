"""phmi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from phmi import views
from projects import urls as project_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("activities", views.ActivityList.as_view(), name="activity-list"),
    path("activities/<slug>", views.ActivityDetail.as_view(), name="activity-detail"),
    path("login", views.GenerateMagicLoginURL.as_view(), name="request-login"),
    path("login/<signed_pk>", views.Login.as_view(), name="login"),
    path("logout", views.Logout.as_view(), name="logout"),
    path(
        "org-types",
        views.OrgTypeList.as_view(),
        name="org-type-list"
    ),
    path(
        "org-types/<slug>",
        views.OrgTypeDetail.as_view(),
        name="org-type-detail"
    ),
]

urlpatterns += project_urls.urlpatterns


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
