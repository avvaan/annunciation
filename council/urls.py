from django.urls import path

from . import views

app_name = "council"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("pending/", views.pending, name="pending"),
    path("request-access/", views.request_access, name="request_access"),
    path("approvals/", views.approvals, name="approvals"),

    path("meetings/", views.meeting_list, name="meeting_list"),
    path("meetings/new/", views.meeting_form, name="meeting_new"),
    path("meetings/<int:pk>/", views.meeting_detail, name="meeting_detail"),
    path("meetings/<int:pk>/edit/", views.meeting_form, name="meeting_edit"),

    path("protocols/", views.protocol_list, name="protocol_list"),
    path("protocols/new/", views.protocol_form, name="protocol_new"),
    path("protocols/<int:pk>/", views.protocol_detail, name="protocol_detail"),
    path("protocols/<int:pk>/edit/", views.protocol_form, name="protocol_edit"),
    path("protocols/<int:pk>/download/", views.protocol_download, name="protocol_download"),

    path("reports/", views.report_list, name="report_list"),
    path("reports/new/", views.report_form, name="report_new"),
    path("reports/<int:pk>/edit/", views.report_form, name="report_edit"),
    path("reports/<int:pk>/download/", views.report_download, name="report_download"),

    path("documents/<int:pk>/", views.document_download, name="document_download"),

    path("tasks/", views.task_list, name="task_list"),
    path("tasks/new/", views.task_form, name="task_new"),
    path("tasks/<int:pk>/edit/", views.task_form, name="task_edit"),
    path("tasks/<int:pk>/toggle/", views.task_toggle, name="task_toggle"),

    path("projects/", views.project_list, name="project_list"),
    path("mailing/", views.mailing, name="mailing"),
]
