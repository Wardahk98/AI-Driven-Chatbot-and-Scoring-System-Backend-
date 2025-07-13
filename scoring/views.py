from uuid import uuid4
from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse, Response
from rest_framework import status
from interview.models import Question,  Response as Answer
from candidate.models import Candidate, CandidateScore
from interview.serializers import QuestionSerializer, CandidateResponseSerializer
from candidate.serializers import CandidateSerializer
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from django.core.paginator import Paginator
from collections import defaultdict
from django.db import IntegrityError
from scoring.utils import compute_candidate_scores


class CandidateScoreView(APIView):
    def post(self, request):
        candidate_id = request.data.get("candidate_id")
        if not candidate_id:
            return DRFResponse({"error": "candidate_id is required."}, status=400)

        candidate = get_object_or_404(Candidate, candidate_id=candidate_id)
        result = compute_candidate_scores(candidate)

        if result is None:
            return DRFResponse({"error": "No answers found for this candidate."}, status=404)

        CandidateScore.objects.update_or_create(
            candidate=candidate,
            defaults={
                "competency_scores": result["competency_scores"],
                "total_score": result["total_score"]
            }
        )

        return DRFResponse({
            "candidate_id": candidate_id,
            **result,
            "message": "Scores computed successfully."
        })



