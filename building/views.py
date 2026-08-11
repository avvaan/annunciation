from django.shortcuts import render

from .models import BuildingProject


def project(request):
    project = BuildingProject.get_solo()
    updates = project.updates.filter(is_published=True)
    photos = project.photos.all()
    return render(request, "building/project.html", {"project": project, "updates": updates, "photos": photos})
