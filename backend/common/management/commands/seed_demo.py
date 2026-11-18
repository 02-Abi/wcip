"""Populate the database with realistic demo data.

Idempotent: running twice will not duplicate rows (lookups by natural
keys). Use ``--reset`` to wipe WCIP data first (does not touch auth
users unless ``--reset-users`` is passed).

Usage:
    python manage.py seed_demo
    python manage.py seed_demo --reset
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.employees.models import Department, Employee
from apps.projects.models import Project, ProjectRequiredSkill
from apps.skills.models import EmployeeSkill, Skill, SkillCategory

User = get_user_model()

DEPARTMENTS = [
    ("ENG", "Engineering"),
    ("DATA", "Data & Analytics"),
    ("OPS", "Operations"),
    ("SALES", "Sales"),
    ("HR", "People & Culture"),
]

SKILL_CATEGORIES = {
    "Languages": ["Python", "JavaScript", "TypeScript", "Java", "Go", "SQL"],
    "Frameworks": ["Django", "React", "FastAPI", "Next.js", "Spring Boot"],
    "Data": ["PostgreSQL", "Pandas", "Spark", "Airflow", "dbt"],
    "Cloud & DevOps": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD"],
    "Product": ["Roadmapping", "User Research", "A/B Testing", "Stakeholder Mgmt"],
    "Soft Skills": ["Communication", "Mentoring", "Project Mgmt"],
}

FIRST_NAMES = [
    "Ada", "Alan", "Grace", "Linus", "Margaret", "Dennis", "Barbara", "Ken",
    "Radia", "Vint", "Katherine", "Tim", "Anita", "Guido", "Frances",
]
LAST_NAMES = [
    "Lovelace", "Turing", "Hopper", "Torvalds", "Hamilton", "Ritchie",
    "Liskov", "Thompson", "Perlman", "Cerf", "Johnson", "Berners-Lee",
    "Borg", "Rossum", "Allen",
]
DESIGNATIONS = {
    "ENG": ["Software Engineer", "Senior Engineer", "Staff Engineer", "Eng Manager"],
    "DATA": ["Data Analyst", "Data Engineer", "Data Scientist", "Analytics Lead"],
    "OPS": ["Ops Analyst", "Ops Manager", "Program Manager"],
    "SALES": ["Account Exec", "Sales Manager", "SDR"],
    "HR": ["Recruiter", "HR Business Partner", "People Ops"],
}

PROJECTS = [
    ("Apollo", "Customer analytics platform rebuild", "ACTIVE", "HIGH", 4),
    ("Gemini", "Internal tooling modernization", "ACTIVE", "MEDIUM", 3),
    ("Orion", "Mobile app v2", "PLANNED", "HIGH", 3),
    ("Vega", "Data warehouse migration", "ACTIVE", "CRITICAL", 2),
    ("Lyra", "Sales enablement revamp", "PLANNED", "MEDIUM", 2),
]

PROFICIENCIES = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]


class Command(BaseCommand):
    help = "Seed realistic demo data for WCIP."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Wipe WCIP data first")
        parser.add_argument(
            "--employees", type=int, default=30, help="How many employees to create"
        )
        parser.add_argument("--seed", type=int, default=42, help="Random seed")

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])
        if options["reset"]:
            self._reset()

        departments = self._departments()
        categories = self._skill_categories()
        employees = self._employees(departments, options["employees"])
        self._skills(departments, categories, employees)
        projects = self._projects()
        self._required_skills(projects, categories)

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
        self.stdout.write(f"  Departments: {Department.objects.count()}")
        self.stdout.write(f"  Employees:   {Employee.objects.count()}")
        self.stdout.write(f"  Skills:      {Skill.objects.count()}")
        self.stdout.write(f"  EmployeeSkill links: {EmployeeSkill.objects.count()}")
        self.stdout.write(f"  Projects:    {Project.objects.count()}")
        self.stdout.write(
            f"  Requirements: {ProjectRequiredSkill.objects.count()}"
        )

    # -- helpers -------------------------------------------------------------

    def _reset(self):
        self.stdout.write("Resetting WCIP data...")
        ProjectRequiredSkill.objects.all().delete()
        Project.objects.all().delete()
        EmployeeSkill.objects.all().delete()
        Skill.objects.all().delete()
        SkillCategory.objects.all().delete()
        Employee.objects.all().delete()
        Department.objects.all().delete()

    def _departments(self):
        result = {}
        for code, name in DEPARTMENTS:
            dept, _ = Department.objects.get_or_create(
                code=code, defaults={"name": name}
            )
            result[code] = dept
        return result

    def _skill_categories(self):
        result = {}
        for cat_name, skill_names in SKILL_CATEGORIES.items():
            cat, _ = SkillCategory.objects.get_or_create(
                name=cat_name, defaults={"description": f"{cat_name} skills"}
            )
            for skill_name in skill_names:
                skill, _ = Skill.objects.get_or_create(
                    category=cat, name=skill_name, defaults={"is_active": True}
                )
                result[skill_name] = skill
        return result

    def _employees(self, departments, count):
        result = []
        existing_ids = set(Employee.objects.values_list("employee_id", flat=True))
        for i in range(count):
            emp_id = f"E{i + 1:04d}"
            if emp_id in existing_ids:
                result.append(Employee.objects.get(employee_id=emp_id))
                continue
            dept_code = random.choice(list(departments))
            dept = departments[dept_code]
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            email = f"{first.lower()}.{last.lower().replace('-', '')}{i}@wcip.demo"
            emp = Employee.objects.create(
                employee_id=emp_id,
                first_name=first,
                last_name=last,
                email=email,
                department=dept,
                designation=random.choice(DESIGNATIONS[dept_code]),
                joining_date=date.today() - timedelta(days=random.randint(30, 2000)),
                employment_status=random.choices(
                    ["ACTIVE", "ON_LEAVE", "TERMINATED"], weights=[85, 10, 5]
                )[0],
                total_experience_years=Decimal(str(round(random.uniform(0.5, 18), 1))),
            )
            result.append(emp)
        return result

    def _skills(self, departments, categories, employees):
        skill_list = list(categories.values())
        for emp in employees:
            # Pick 3-7 skills, weighted toward active employees
            n = random.randint(3, 7)
            chosen = random.sample(skill_list, n)
            for skill in chosen:
                prof = random.choices(
                    PROFICIENCIES, weights=[30, 40, 20, 10]
                )[0]
                years = {
                    "BEGINNER": (0, 1),
                    "INTERMEDIATE": (1, 3),
                    "ADVANCED": (3, 6),
                    "EXPERT": (5, 12),
                }[prof]
                EmployeeSkill.objects.get_or_create(
                    employee=emp,
                    skill=skill,
                    defaults={
                        "proficiency": prof,
                        "years_experience": Decimal(
                            str(round(random.uniform(*years), 1))
                        ),
                        "is_verified": random.random() < 0.4,
                    },
                )

    def _projects(self):
        result = []
        for name, desc, status, priority, headcount in PROJECTS:
            proj, _ = Project.objects.get_or_create(
                name=name,
                defaults={
                    "description": desc,
                    "status": status,
                    "priority": priority,
                    "headcount_needed": headcount,
                    "start_date": date.today() + timedelta(days=random.randint(-60, 60)),
                    "end_date": date.today() + timedelta(days=random.randint(120, 400)),
                },
            )
            result.append(proj)
        return result

    def _required_skills(self, projects, categories):
        skill_list = list(categories.values())
        for proj in projects:
            n = random.randint(2, 4)
            for skill in random.sample(skill_list, n):
                ProjectRequiredSkill.objects.get_or_create(
                    project=proj,
                    skill=skill,
                    defaults={
                        "minimum_proficiency": random.choices(
                            PROFICIENCIES, weights=[10, 40, 35, 15]
                        )[0],
                        "minimum_years": Decimal(str(round(random.uniform(0, 5), 1))),
                        "is_mandatory": random.random() < 0.7,
                        "weight": Decimal(str(round(random.uniform(0.5, 3.0), 2))),
                    },
                )
