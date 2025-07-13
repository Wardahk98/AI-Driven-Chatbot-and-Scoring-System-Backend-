from django.contrib.postgres.fields import ArrayField
from django.db import models
import uuid

from rest_framework.exceptions import ValidationError


class AcademicProgram(models.Model):
    name = models.CharField(max_length=255, unique=True)
    department = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class JobPosition(models.Model):
    title = models.CharField(max_length=255, unique=True)
    department = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


def generate_candidate_id():
    return f"cand-{uuid.uuid4().hex[:8]}"


class Candidate(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    INTERVIEW_TYPE_CHOICES = [
        ('hr', 'HR Interview'),
        ('academic', 'Academic Interview'),
    ]

    APPLICATION_TYPE_CHOICES = [
        ('program', 'Academic Program'),
        ('position', 'Job Position'),
    ]

    candidate_id = models.CharField(max_length=100, unique=True, default=generate_candidate_id)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    cnic = models.CharField(max_length=25, unique=True)
    application_type = models.CharField(
        max_length=20, choices=APPLICATION_TYPE_CHOICES, default='program'
    )

    academic_program = models.ForeignKey(
        AcademicProgram, on_delete=models.SET_NULL, null=True, blank=True
    )
    job_position = models.ForeignKey(
        JobPosition, on_delete=models.SET_NULL, null=True, blank=True
    )

    interview_type = models.CharField(
        max_length=20, choices=INTERVIEW_TYPE_CHOICES, default='hr'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='not_started'
    )
    invite_token = models.UUIDField(unique=True, null=True, blank=True, editable=False)
    is_invited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_question_index = models.IntegerField(default=0)
    interview_started_at = models.DateTimeField(null=True, blank=True)
    interview_ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.applied_to}"

    def clean(self):
        if self.academic_program and self.job_position:
            raise ValidationError("A candidate cannot apply to both a program and a job.")
        if not self.academic_program and not self.job_position:
            raise ValidationError("A candidate must apply to either a program or a job.")

    @property
    def applied_to_display(self):
        if self.academic_program:
            return f"{self.academic_program.name} (Program)"
        elif self.job_position:
            return f"{self.job_position.title} (Position)"
        return "N/A"





class CandidateScore(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name="score")
    competency_scores = models.JSONField(default=dict)  # e.g., {"Motivation & Intent": 4}
    total_score = models.FloatField(default=0.0)
    scored_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.name} - Total Score: {self.total_score}"
