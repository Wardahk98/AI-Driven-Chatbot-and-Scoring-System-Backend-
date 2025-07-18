from rest_framework import serializers
from interview.models import Question,  Response as Answer
from candidate.models import Candidate, CandidateScore

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

