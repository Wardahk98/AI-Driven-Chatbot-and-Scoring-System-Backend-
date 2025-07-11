from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse, Response
from rest_framework import status
from interview.models import Question, Candidate, Response as Answer, CandidateScore
from interview.serializers import QuestionSerializer, CandidateResponseSerializer, CandidateSerializer
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from django.core.paginator import Paginator
from collections import defaultdict
from django.db import IntegrityError

class InterviewView(APIView):
    def get(self, request):
        interview_type = request.GET.get('type')
        if not interview_type:
            return DRFResponse({"error": "Missing 'type' query parameter (hr or academic)"}, status=400)

        questions = Question.objects.filter(type=interview_type)
        serializer = QuestionSerializer(questions, many=True)
        return DRFResponse({
            "interview_type": interview_type,
            "questions": serializer.data
        })

    def post(self, request):
        serializer = CandidateResponseSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            candidate, _ = Candidate.objects.get_or_create(candidate_id=data['candidate_id'], defaults={'name': data.get('name', '')})

            for item in data['responses']:
                question = get_object_or_404(Question, id=item['question_id'])
                Answer.objects.create(candidate=candidate, question=question, answer=item['answer'])

            return DRFResponse({"status": "success", "message": "Responses saved successfully."})
        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CandidateListView(APIView):
    def get(self, request):
        candidates = Candidate.objects.all()
        data = []

        for c in candidates:
            responses = Answer.objects.filter(candidate=c).order_by('created_at')
            if responses.exists():
                interview_type = responses.first().question.type
                submitted_on = localtime(responses.first().created_at).strftime('%Y-%m-%d %H:%M')
                data.append({
                    'candidate_id': c.candidate_id,
                    'name': c.name,
                    'interview_type': interview_type,
                    'submitted_on': submitted_on,
                })

        return DRFResponse(data)

class CandidateDetailView(APIView):
    def get(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, candidate_id=candidate_id)
        responses = Answer.objects.filter(candidate=candidate).select_related('question')

        data = {
            'candidate_id': candidate.candidate_id,
            'name': candidate.name,
            'email': candidate.email,
            'CNIC': candidate.cnic,
            'interview_type': candidate.interview_type,
            'responses': [
                {
                    'question': r.question.text,
                    'competency': r.question.competencies,
                    'answer': r.answer,
                }
                for r in responses
            ]
        }

        return DRFResponse(data)

class DashboardStatsView(APIView):
    def get(self, request):
        candidates = Candidate.objects.all()
        total = candidates.count()
        hr = 0
        academic = 0

        for c in candidates:
            responses = Answer.objects.filter(candidate=c)
            if responses.exists():
                if responses.first().question.type == 'hr':
                    hr += 1
                else:
                    academic += 1

        return DRFResponse({
            'total_candidates': total,
            'hr_interviews': hr,
            'academic_interviews': academic
        })

class AnalyticsView(APIView):
    def get(self, request):
        total = Candidate.objects.count()
        completed = Candidate.objects.filter(status='completed').count()
        in_progress = Candidate.objects.filter(status='in_progress').count()
        not_started = Candidate.objects.filter(status='not_started').count()

        return Response({
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started
        })

class CandidateTableView(APIView):
    def get(self, request):
        status_filter = request.GET.get('status')
        page = int(request.GET.get('page', 1))

        candidates = Candidate.objects.all().order_by('-id')
        if status_filter:
            candidates = candidates.filter(status=status_filter)

        paginator = Paginator(candidates, 10)
        page_obj = paginator.get_page(page)

        COMPETENCY_KEYS = {
            'motivation & intent': 'Motivation & Intent',
            'teamwork': 'Teamwork',
            'communication & feedback': 'Communication & Feedback',
            'value & inclusion': 'Value & Inclusion',
            'self-reflection': 'Self-Reflection',
        }

        data = []
        for candidate in page_obj:
            responses = Answer.objects.filter(candidate=candidate).select_related('question')

            # Default all to None
            competency_answers = {v: '' for v in COMPETENCY_KEYS.values()}

            for r in responses:
                key = COMPETENCY_KEYS.get(r.question.competencies)
                if key:
                    competency_answers[key] = r.answer

            data.append({
                "candidate_id": candidate.candidate_id,
                "name": candidate.name,
                "email": getattr(candidate, "email", "N/A"),
                "status": candidate.status,
                "competency_answers": competency_answers
            })

        return DRFResponse({
            "results": data,
            "page": page,
            "total_pages": paginator.num_pages
        })

class CandidateSignupView(APIView):
    def post(self, request):
        serializer = CandidateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return DRFResponse({'message': 'Signup successful'}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return DRFResponse({'error': 'Candidate with this ID, email, or CNIC already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
