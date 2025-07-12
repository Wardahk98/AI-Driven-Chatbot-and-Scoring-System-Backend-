from rest_framework import serializers
from interview.models import Question,  Response as Answer
from candidate.models import Candidate, CandidateScore


class CandidateDashboardSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    competency_answers = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'candidate_id', 'full_name', 'email', 'status', 'interview_type',
            'competency_answers'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_competency_answers(self, obj):
        answers = Answer.objects.filter(candidate=obj).select_related('question').order_by('created_at')
        result = {}

        for ans in answers:
            competency = ans.question.competencies
            if competency not in result:
                result[competency] = []
            result[competency].append(ans.answer)

        return result

class CandidateDetailDashboardSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    responses = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'candidate_id', 'full_name', 'email', 'cnic',
            'interview_type', 'status', 'responses'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_responses(self, obj):
        answers = Answer.objects.filter(candidate=obj).select_related('question')
        return [
            {
                'question': ans.question.text,
                'competency': ans.question.competencies,
                'answer': ans.answer,
            }
            for ans in answers
        ]

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'competencies', 'text', 'is_open_ended']

class ResponseItemSerializer(serializers.Serializer):
    question_id = serializers.CharField()
    answer = serializers.CharField()

class CandidateResponseSerializer(serializers.Serializer):
    candidate_id = serializers.CharField()
    name = serializers.CharField(required=False, allow_blank=True)
    interview_type = serializers.ChoiceField(choices=['hr', 'academic'])
    responses = ResponseItemSerializer(many=True)


