from django.urls import path
from dashboard.views import (
    DashboardStatsView,
    AnalyticsView,
    CandidateTableView,
    CandidateDetailView,
    CandidateCSVUploadView,
    CandidateScoreCSVDownloadView
)


urlpatterns = [
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('candidates-table/', CandidateTableView.as_view()),
    path('candidates/<str:candidate_id>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('upload-candidates/', CandidateCSVUploadView.as_view(), name='upload-csv'),
    path('download-scores/', CandidateScoreCSVDownloadView.as_view(), name='download-csv'),
]