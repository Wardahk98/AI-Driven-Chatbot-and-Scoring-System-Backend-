from django.urls import path
from scoring.views import (
    CandidateScoreView

)


urlpatterns = [
    path('score/', CandidateScoreView.as_view(), name='candidate-scoring')
]