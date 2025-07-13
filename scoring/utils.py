from interview.models import Question,  Response as Answer


def compute_candidate_scores(candidate):
    answers = Answer.objects.filter(candidate=candidate).select_related('question')
    if not answers.exists():
        return None

    individual_scores = []
    competency_scores = {}

    for r in answers:
        comp = r.question.competencies
        # score = get_score_from_llm(question.text, r.answer)
        score = 4.0  # TODO: Replace with LLM later

        r.score = score
        r.save()

        competency_scores.setdefault(comp, []).append(score)

        individual_scores.append({
            "question": r.question.text,
            "competency": comp,
            "answer": r.answer,
            "score": score
        })

    averaged = {
        k: round(sum(v) / len(v), 2)
        for k, v in competency_scores.items()
    }

    total_score = round(sum(averaged.values()) / len(averaged), 2)

    return {
        "individual_scores": individual_scores,
        "competency_scores": averaged,
        "total_score": total_score
    }
