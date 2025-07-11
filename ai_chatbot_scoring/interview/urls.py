from django.urls import path
from interview.views import (
    InterviewView,
    CandidateListView,
    CandidateDetailView,
    DashboardStatsView,
    AnalyticsView,
    CandidateTableView,
    CandidateSignupView,
    CandidateScoreView
)


urlpatterns = [
    path('interview/', InterviewView.as_view()),
    path('candidates/', CandidateListView.as_view(), name='candidate-list'),
    path('candidates/<str:candidate_id>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('candidates-table/', CandidateTableView.as_view()),
    path('register/', CandidateSignupView.as_view(), name='candidate-signup'),
    path('score/', CandidateScoreView.as_view(), name='candidate-scoring')
]