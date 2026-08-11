from django.urls import path

from . import views

app_name = "school"

urlpatterns = [
    path("", views.school_page, name="page"),
]
