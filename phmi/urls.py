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

from .views import (
    GenerateMagicLoginURL, GroupAdd, GroupDetail, GroupEdit,
    Home, Login, Logout
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", Home.as_view(), name="home"),
    path("login", GenerateMagicLoginURL.as_view(), name="request-login"),
    path("login/<signed_pk>", Login.as_view(), name="login"),
    path("logout", Logout.as_view(), name="logout"),
    path("groups/add", GroupAdd.as_view(), name="group-add"),
    path("groups/<int:pk>", GroupDetail.as_view(), name="group-detail"),
    path(
        "groups/<int:pk>/edit", GroupEdit.as_view(), name="group-edit"
    ),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
