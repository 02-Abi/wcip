from django.urls import path
from .views import project_matches

urlpatterns = [
    path("projects/<uuid:project_id>/matches/", project_matches, name="project-matches"),
]
