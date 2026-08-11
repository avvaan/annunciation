from django.urls import path

from . import views

app_name = "commemorations"

urlpatterns = [
    path("", views.submit, name="submit"),
    path("batch/<int:pk>/pdf/", views.batch_pdf, name="batch_pdf"),
]
