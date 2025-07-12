from uuid import uuid4, UUID

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse, Response
from rest_framework import status
from interview.models import Question,  Response as Answer
from candidate.models import Candidate, CandidateScore, AcademicProgram, JobPosition
from interview.serializers import QuestionSerializer, CandidateResponseSerializer
from candidate.serializers import CandidateSerializer, CandidateSignupSerializer, AcademicProgramSerializer, JobPositionSerializer
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from django.core.paginator import Paginator
from collections import defaultdict
from django.db import IntegrityError
from services.email import send_invite_link

class CandidateSignupView(APIView):
    def post(self, request, token):
        try:
            candidate = Candidate.objects.get(invite_token=UUID(token), is_invited=True)
        except Candidate.DoesNotExist:
            return DRFResponse({'error': 'Invalid or expired token.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CandidateSignupSerializer(candidate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return DRFResponse({'message': 'Signup successful'}, status=status.HTTP_200_OK)
        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CandidateLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        cnic = request.data.get('cnic')

        try:
            candidate = Candidate.objects.get(email=email, cnic=cnic)
            if not candidate.is_invited:
                return DRFResponse({"error": "You are not invited yet."}, status=403)

            return DRFResponse({
                "message": "Login successful",
                "candidate_id": candidate.candidate_id,
                "interview_type": candidate.interview_type,
                "status": candidate.status,
            })
        except Candidate.DoesNotExist:
            return DRFResponse({"error": "Invalid credentials."}, status=401)

class SendInviteView(APIView):
    def post(self, request):
        # Accept either a single candidate_id or a list
        candidate_ids = request.data.get("candidate_ids")
        if not candidate_ids:
            return DRFResponse({"error": "candidate_ids is required."}, status=400)

        # Normalize to list
        if isinstance(candidate_ids, str):
            candidate_ids = [candidate_ids]

        invited = []
        not_found = []
        failed = []

        for cid in candidate_ids:
            try:
                candidate = Candidate.objects.get(candidate_id=cid)

                if not candidate.invite_token:
                    candidate.invite_token = uuid4()
                candidate.is_invited = True
                candidate.save()

                invite_url = f"https://yourdomain.com/signup/{candidate.invite_token}/"

                try:
                    send_invite_link(candidate.email, invite_url)
                    invited.append(cid)
                except Exception as e:
                    failed.append({"candidate_id": cid, "error": str(e)})

            except Candidate.DoesNotExist:
                not_found.append(cid)

        return DRFResponse({
            "invited": invited,
            "not_found": not_found,
            "failed": failed,
            "message": f"Processed {len(candidate_ids)} candidate(s)."
        }, status=200)


class AcademicProgramListView(ListAPIView):
    queryset = AcademicProgram.objects.filter(is_active=True)
    serializer_class = AcademicProgramSerializer


class JobPositionListView(ListAPIView):
    queryset = JobPosition.objects.filter(is_active=True)
    serializer_class = JobPositionSerializer


