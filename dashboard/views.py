from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse, Response
from rest_framework.parsers import MultiPartParser
from django.db import IntegrityError
from rest_framework import status
from interview.models import Question,  Response as Answer
from candidate.models import Candidate, CandidateScore, AcademicProgram, JobPosition
from interview.serializers import QuestionSerializer, CandidateResponseSerializer
from candidate.serializers import CandidateSerializer
from dashboard.serializers import CandidateDashboardSerializer, CandidateDetailDashboardSerializer
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from django.core.paginator import Paginator
from collections import defaultdict
from django.db import IntegrityError
from django.http import HttpResponse
import csv
import io

class DashboardStatsView(APIView):
    def get(self, request):
        total = Candidate.objects.count()
        hr = Candidate.objects.filter(interview_type='hr').filter(answer__isnull=False).distinct().count()
        academic = Candidate.objects.filter(interview_type='academic').filter(answer__isnull=False).distinct().count()

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

        return DRFResponse({
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started
        })

class CandidateTableView(APIView):
    def get(self, request):
        status_filter = request.GET.get('status')
        page = int(request.GET.get('page', 1))

        candidates = Candidate.objects.all().order_by('-created_at')
        if status_filter:
            candidates = candidates.filter(status=status_filter)

        paginator = Paginator(candidates, 10)
        page_obj = paginator.get_page(page)

        data = CandidateDashboardSerializer(page_obj, many=True).data

        return DRFResponse({
            "results": data,
            "page": page,
            "total_pages": paginator.num_pages
        })

class CandidateDetailView(APIView):
    def get(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, candidate_id=candidate_id)
        data = CandidateDetailDashboardSerializer(candidate).data
        return DRFResponse(data)

class CandidateCSVUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj or not file_obj.name.endswith('.csv'):
            return DRFResponse({"error": "Please upload a valid CSV file."}, status=400)

        decoded_file = file_obj.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        created = []
        failed = []

        for row in reader:
            try:
                # Required fields
                first_name = row.get('first_name')
                last_name = row.get('last_name')
                email = row.get('email')
                cnic = row.get('cnic')
                interview_type = row.get('interview_type', 'hr')
                application_type = row.get('application_type', 'program').lower()
                applied_to = row.get('applied_to')  # program or position name

                if application_type == 'program':
                    program = AcademicProgram.objects.filter(name__iexact=applied_to).first()
                    position = None
                else:
                    program = None
                    position = JobPosition.objects.filter(title__iexact=applied_to).first()

                candidate = Candidate.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    cnic=cnic,
                    interview_type=interview_type,
                    application_type=application_type,
                    # applied_to=applied_to,
                    academic_program=program,
                    job_position=position
                )
                created.append(candidate.email)
            except IntegrityError:
                failed.append({"email": row.get("email"), "error": "Duplicate email or CNIC"})
            except Exception as e:
                failed.append({"email": row.get("email"), "error": str(e)})

        return DRFResponse({
            "created": created,
            "failed": failed,
            "message": f"Processed {len(created) + len(failed)} records"
        }, status=200)

class CandidateScoreCSVDownloadView(APIView):
    def get(self, request):
        candidates = Candidate.objects.filter(score__isnull=False).select_related('score')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="candidate_scores.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Candidate ID', 'Name', 'Email', 'Interview Type',
            'Total Score', 'Competency', 'Score'
        ])

        for c in candidates:
            full_name = f"{c.first_name} {c.last_name}"
            for comp, score in c.score.competency_scores.items():
                writer.writerow([
                    c.candidate_id,
                    full_name,
                    c.email,
                    c.interview_type,
                    c.score.total_score,
                    comp,
                    score
                ])

        return response
