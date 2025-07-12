from django.urls import path
from interview.views import (
    InterviewView
)


urlpatterns = [
    path('interview/', InterviewView.as_view())
]