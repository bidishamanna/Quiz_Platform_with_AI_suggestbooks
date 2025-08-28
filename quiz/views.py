from django.shortcuts import render
from django.http import JsonResponse
from .models import Question, UserAnswer
from django.views.decorators.csrf import csrf_exempt
import json

def take_test(request):
    return render(request, 'quiz/question.html')

def get_questions(request):
    questions = Question.objects.all().order_by('id')
    data = []
    for q in questions:
        data.append({
            'id': q.id,
            'text': q.text,
            'option1': q.option1,
            'option2': q.option2,
            'option3': q.option3,
            'option4': q.option4
        })
    return JsonResponse({'questions': data})


def submit_answer_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body) # Reads the raw request body, which comes in as a JSON string from the frontend.
# Parses it using json.loads() to convert it into a Python dictionary (data).
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')

        question = Question.objects.get(id=question_id)
        is_correct = int(selected_option) == question.correct_option

        UserAnswer.objects.create(
            question=question,
            selected_option=selected_option,
            is_correct=is_correct
        )

        return JsonResponse({'success': True, 'is_correct': is_correct})
    return JsonResponse({'error': 'Invalid request'}, status=400)



def test_template(request):
    return render(request,'quiz/start_test.html')

