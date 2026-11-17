from rest_framework.routers import DefaultRouter
from .views import SkillCategoryViewSet, SkillViewSet, EmployeeSkillViewSet

router = DefaultRouter()
router.register(r"skill-categories", SkillCategoryViewSet, basename="skill-category")
router.register(r"skills", SkillViewSet, basename="skill")
router.register(r"employee-skills", EmployeeSkillViewSet, basename="employee-skill")

urlpatterns = router.urls
