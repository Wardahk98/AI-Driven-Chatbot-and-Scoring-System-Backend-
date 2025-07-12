from django.urls import path
from candidate.views import (
    CandidateSignupView,
    CandidateLoginView,
    SendInviteView,
    AcademicProgramListView,
    JobPositionListView
)


urlpatterns = [
    path('signup/<token>/', CandidateSignupView.as_view(), name='candidate-signup'),
    path('login/', CandidateLoginView.as_view(), name='candidate-signup'),
    path('invite/', SendInviteView.as_view(), name='send-invite'),
    path('programs/', AcademicProgramListView.as_view(), name='program-list'),
    path('positions/', JobPositionListView.as_view(), name='position-list'),
]