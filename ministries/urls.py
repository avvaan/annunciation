from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "ministries"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="ministries/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="ministries:ministry_list"), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("", views.ministry_list, name="ministry_list"),
    path("<str:slug>/", views.ministry_detail, name="ministry_detail"),
    path("<str:slug>/join/", views.ministry_join, name="ministry_join"),
    path("<str:slug>/leave/", views.ministry_leave, name="ministry_leave"),
    path("membership/<int:pk>/approve/", views.membership_approve, name="membership_approve"),
    path("topic/<int:pk>/", views.topic_detail, name="topic_detail"),
    path("supply/<int:pk>/done/", views.supply_toggle, name="supply_toggle"),
    path("document/<int:pk>/", views.document_download, name="document_download"),
    path("report/<int:pk>/", views.report_download, name="report_download"),
]
