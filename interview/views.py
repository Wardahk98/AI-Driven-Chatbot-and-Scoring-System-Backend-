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
import random
import openai
import requests
from django.conf import settings

DEFAULT_FOLLOW_UPS = [
    "That's a thoughtful answer.",
    "Interesting, care to elaborate?",
    "Thanks for sharing that.",
    "You're doing great!",
    "That’s a fantastic perspective.",
    "I appreciate the detail in your response.",
    "That's very insightful.",
    "Excellent! Let’s move to the next one.",
]





def get_llm_follow_up(interview_type ,question_text, candidate_answer):
    prompt = (
        f"You are an interview assistant. The candidate is giving interview for {interview_type}. "
        f"The candidate was asked:\n"
        f"'{question_text}'\n"
        f"They answered:\n"
        f"'{candidate_answer}'\n"
        f"Reply with a short, polite, human-like follow-up message, "
        f"not asking for clarifications just a polite acknowledgement of the answer the candiadate provided "
        f" 5-6 words only."
    )


    headers = {
        "Authorization": f"Bearer {settings.OPENAI}",  # Replace with your OpenRouter key
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 50
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("LLM Error:", e)
        return "Thank you for your answer!"



class InterviewView(APIView):
    def get(self, request):
        candidate_id = request.GET.get('candidate_id')
        interview_type = request.GET.get('type')
        question_index = int(request.GET.get('index', 0))

        if not candidate_id or not interview_type:
            return DRFResponse({"error": "Missing 'candidate_id' or 'type'"}, status=400)

        # Get questions for this interview type
        questions = Question.objects.filter(type=interview_type, is_active=True).order_by('id')

        if question_index >= len(questions):
            return DRFResponse({"done": True, "message": "Interview complete!"})

        q = questions[question_index]

        return DRFResponse({
            "index": question_index,
            "question_id": q.id,
            "text": q.text,
            "is_open_ended": q.is_open_ended,
            "options": q.options if not q.is_open_ended else [],
            "follow_up_prompt": q.follow_up_prompt or "Thank you! Let's move on."
        })

    def post(self, request):
        serializer = CandidateResponseSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            candidate, _ = Candidate.objects.get_or_create(
                candidate_id=data['candidate_id'],
                defaults={'name': data.get('name', '')}
            )

            for item in data['responses']:
                question = get_object_or_404(Question, id=item['question_id'])
                Answer.objects.update_or_create(
                    candidate=candidate,
                    question=question,
                    defaults={'answer': item['answer']}
                )
                print(data['interview_type'])

                feedback = get_llm_follow_up(data['interview_type'],question.text, item['answer'])

            return DRFResponse({
                "status": "success",
                "message": "Response saved successfully.",
                "next_prompt": feedback
            })

        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
