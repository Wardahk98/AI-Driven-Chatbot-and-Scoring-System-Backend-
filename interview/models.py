from django.contrib.postgres.fields import ArrayField
from django.db import models
import uuid
from candidate.models import Candidate


class Question(models.Model):
    INTERVIEW_TYPES = [
        ('hr', 'HR'),
        ('academic', 'Academic'),
    ]
    COMPETENCIES=[
        ('motivation & intent','Motivation & Intent'),
        ('teamwork', 'Teamwork'),
        ('communication & feedback', 'Communication & Feedback'),
        ('value & inclusion', 'Value & Inclusion'),
        ('self-reflection','Self-Reflection'),

    ]
    #question_id = models.CharField(max_length=10, unique=True)
    competencies = models.CharField(max_length=50, choices=COMPETENCIES)
    text = models.TextField()
    type = models.CharField(max_length=20, choices=INTERVIEW_TYPES)
    is_open_ended = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    follow_up_prompt = models.CharField(
        max_length=255,
        blank=True,
        help_text="E.g., 'That's insightful! Want to elaborate?'"
    )

    options = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        null=True,
        help_text="Only for multiple choice questions"
    )

    def __str__(self):
        return f"{self.id} ({self.type})"


class Response(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate} - {self.question}"

