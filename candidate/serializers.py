from rest_framework import serializers
from interview.models import Question,  Response as Answer
from candidate.models import Candidate, CandidateScore, AcademicProgram, JobPosition


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            'candidate_id', 'first_name', 'last_name', 'email',
            'cnic', 'application_type', 'applied_to',
            'interview_type', 'status'
        ]

    def get_applied_to(self, obj):
        return obj.applied_to_display


class CandidateSignupSerializer(serializers.ModelSerializer):
    academic_program_id = serializers.IntegerField(required=False)
    job_position_id = serializers.IntegerField(required=False)

    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'email', 'cnic', 'academic_program_id', 'job_position_id']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.cnic = validated_data.get('cnic', instance.cnic)

        program_id = validated_data.get('academic_program_id')
        position_id = validated_data.get('job_position_id')

        if program_id and position_id:
            raise serializers.ValidationError("Cannot select both a program and a position.")
        if not program_id and not position_id:
            raise serializers.ValidationError("Either academic_program_id or job_position_id must be provided.")

        if program_id:
            instance.academic_program_id = program_id
            instance.job_position = None
            instance.application_type = 'program'
        elif position_id:
            instance.job_position_id = position_id
            instance.academic_program = None
            instance.application_type = 'position'

        instance.status = 'in_progress'
        instance.save()
        return instance


class AcademicProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicProgram
        fields = ['id', 'name', 'department']


class JobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = ['id', 'title', 'department']
