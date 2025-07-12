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


class CandidateScoreView(APIView):
    def post(self, request):
        candidate_id = request.data.get("candidate_id")
        if not candidate_id:
            return DRFResponse({"error": "candidate_id is required."}, status=400)

        candidate = get_object_or_404(Candidate, candidate_id=candidate_id)
        answers = Answer.objects.filter(candidate=candidate).select_related('question')

        if not answers.exists():
            return DRFResponse({"error": "No answers found for this candidate."}, status=404)

        individual_scores = []
        competency_scores = {}

        for r in answers:
            comp = r.question.competencies

            # Dummy score (replace with LLM later)
            score = 4.0  # TODO: replace with LLM output

            # Save score in each answer
            r.score = score
            r.save()

            # Track scores per competency
            if comp not in competency_scores:
                competency_scores[comp] = []
            competency_scores[comp].append(score)

            # Collect answer-level info
            individual_scores.append({
                "question": r.question.text,
                "competency": comp,
                "answer": r.answer,
                "score": score
            })

        # Compute avg per competency
        averaged = {
            k: round(sum(v) / len(v), 2)
            for k, v in competency_scores.items()
        }

        total_score = round(sum(averaged.values()) / len(averaged), 2)

        # Save to CandidateScore
        CandidateScore.objects.update_or_create(
            candidate=candidate,
            defaults={
                "competency_scores": averaged,
                "total_score": total_score
            }
        )

        return DRFResponse({
            "candidate_id": candidate_id,
            "individual_scores": individual_scores,
            "competency_scores": averaged,
            "total_score": total_score,
            "message": "Scores computed successfully."
        })


