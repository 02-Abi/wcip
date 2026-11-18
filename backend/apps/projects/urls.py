from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectRequiredSkillViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"project-required-skills", ProjectRequiredSkillViewSet, basename="project-required-skill")

urlpatterns = router.urls
