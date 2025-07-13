from datetime import timezone
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
from django.core.cache import cache
import hashlib


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

def get_llm_follow_up(interview_type, question_text, candidate_answer):
    # Hash the answer text for consistent key
    answer_hash = hashlib.md5(candidate_answer.encode('utf-8')).hexdigest()
    cache_key = f"llm_followup_q{question_text[:50]}_{answer_hash}"

    # Check cache first
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response

    # If not cached, generate prompt
    prompt = (
        f"You are a polite and professional AI interview assistant conducting a {interview_type} interview.\n"
        f"The candidate was asked:\n"
        f"\"{question_text}\"\n"
        f"The candidate answered:\n"
        f"\"{candidate_answer}\"\n"
        f"Respond with a short, friendly acknowledgment of the candidate’s answer. "
        f"Keep the response natural, polite, and human-like, between 5 to 7 words. "
        f"Do not ask any questions or follow-up."
    )

    headers = {
        "Authorization": f"Bearer {settings.OPENAI}",
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
        content = response.json()['choices'][0]['message']['content'].strip()

        # Store in cache for 1 day (86400 seconds)
        cache.set(cache_key, content, timeout=86400)
        return content

    except Exception as e:
        print("LLM Error:", e)
        return random.choice(DEFAULT_FOLLOW_UPS)



class InterviewView(APIView):
    def get(self, request):
        candidate_id = request.GET.get('candidate_id')
        interview_type = request.GET.get('type')

        if not candidate_id or not interview_type:
            return DRFResponse({"error": "Missing 'candidate_id' or 'type'"}, status=400)

        candidate = get_object_or_404(Candidate, candidate_id=candidate_id)

        # Optional: Start interview time
        if not candidate.interview_started_at:
            candidate.interview_started_at = timezone.now()
            candidate.save()

        questions = Question.objects.filter(type=interview_type, is_active=True).order_by('id')

        if candidate.current_question_index >= len(questions):
            # End timestamp if interview is completed
            if not candidate.interview_ended_at:
                candidate.interview_ended_at = timezone.now()
                candidate.status = 'completed'
                candidate.save()
            return DRFResponse({"done": True, "message": "Interview complete!"})

        q = questions[candidate.current_question_index]

        return DRFResponse({
            "index": candidate.current_question_index,
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
                if Answer.objects.filter(candidate=candidate, question=question).exists():
                    return DRFResponse({
                        "error": f"Answer already submitted for question ID {question.id}."
                    }, status=400)
                Answer.objects.update_or_create(
                    candidate=candidate,
                    question=question,
                    defaults={'answer': item['answer']}
                )
                print(data['interview_type'])

            feedback = get_llm_follow_up(data['interview_type'],question.text, item['answer'])
            candidate.current_question_index += 1
            candidate.save()

            return DRFResponse({
                "status": "success",
                "message": "Response saved successfully.",
                "next_prompt": feedback
            })

        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
