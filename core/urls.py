from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("first-visit/", views.first_visit, name="first_visit"),
    path("clergy/", views.clergy, name="clergy"),
    path("donation/", views.donation, name="donation"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]
