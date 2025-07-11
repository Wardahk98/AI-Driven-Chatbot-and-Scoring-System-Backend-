from rest_framework import serializers
from .models import Question, Candidate, Response

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

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['candidate_id', 'name', 'email', 'cnic', 'interview_type', 'status']
