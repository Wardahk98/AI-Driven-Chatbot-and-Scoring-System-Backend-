from django.contrib.postgres.fields import ArrayField
from django.db import models

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
    candidate_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    cnic = models.CharField(max_length=254, unique=True)
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES, default='hr')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    def __str__(self):
        return self.candidate_id


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

class CandidateScore(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name="score")
    competency_scores = models.JSONField(default=dict)  # e.g., {"Motivation & Intent": 4}
    total_score = models.FloatField(default=0.0)
    scored_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.name} - Total Score: {self.total_score}"