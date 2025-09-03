from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from account.decorators import jwt_required, role_required
from category.models import Category
from subject.models import Subject
from question_sets.models import Set
from .models import Question
import csv
import pandas as pd
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from account.decorators import jwt_required, role_required
from category.models import Category
from subject.models import Subject
from question_sets.models import Set
from .models import Question
import csv
import pandas as pd

# ------------------------------
# Upload Questions (CSV/Excel)
# ------------------------------

@jwt_required
@role_required('staff')
@require_http_methods(["GET", "POST"])
def upload_questions(request):
    if request.method == "GET":
        categories = Category.objects.filter(delflag=False)
        subjects = Subject.objects.filter(delflag=False)
        sets = Set.objects.filter(user=request.user, delflag=False)
        questions = Question.objects.filter(user=request.user, delflag=False).order_by('id')
        return render(request, "questions/csv_question_file_upload.html", {
            "categories": categories,
            "subjects": subjects,
            "sets": sets,
            "questions": questions,
            "user_role": request.user.role,
            "user": request.user,
        })

    # POST request
    uploaded_file = request.FILES.get("file")
    subject_id = request.POST.get("subject")
    set_id = request.POST.get("set")  # Single set

    if not uploaded_file or not subject_id or not set_id:
        return JsonResponse({"message": "File and all selections are required."}, status=400)

    try:
        subject = get_object_or_404(Subject, id=subject_id, delflag=False)
        set_obj = get_object_or_404(Set, id=set_id, user=request.user, delflag=False)

        # Detect file type
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext == "csv":
            decoded_file = uploaded_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            rows = list(reader)
        elif ext in ["xls", "xlsx"]:
            df = pd.read_excel(uploaded_file)
            rows = df.to_dict(orient="records")
        else:
            return JsonResponse({"message": "Unsupported file format. Use CSV or Excel."}, status=400)

        for row in rows:
            question_text = row.get("question_text", "").strip()
            option_a = row.get("option_a", "").strip()
            option_b = row.get("option_b", "").strip()
            option_c = row.get("option_c", "").strip()
            option_d = row.get("option_d", "").strip()
            correct_option = row.get("correct_option", "").strip().upper()
            difficulty_score = row.get("difficulty_score", "").strip()  # New field

            if not all([question_text, option_a, option_b, option_c, option_d, correct_option, difficulty_score]):
                continue  # Skip incomplete rows

            # Validate difficulty_score
            try:
                difficulty_score = Decimal(difficulty_score)
                if not (Decimal('0.10') <= difficulty_score <= Decimal('0.90')):
                    difficulty_score = Decimal('0.50')  # default if out of range
            except (InvalidOperation, TypeError):
                difficulty_score = Decimal('0.50')  # default if invalid

            # Check soft-deleted duplicate
            soft_deleted = Question.objects.filter(
                question_text=question_text,
                subject=subject,
                set=set_obj,
                user=request.user,
                delflag=True
            ).first()

            if soft_deleted:
                soft_deleted.option_a = option_a
                soft_deleted.option_b = option_b
                soft_deleted.option_c = option_c
                soft_deleted.option_d = option_d
                soft_deleted.correct_option = correct_option
                soft_deleted.difficulty_score = difficulty_score
                soft_deleted.delflag = False
                soft_deleted.save()
            else:
                Question.objects.create(
                    subject=subject,
                    set=set_obj,
                    user=request.user,
                    question_text=question_text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_option=correct_option,
                    difficulty_score=difficulty_score
                )

        # Fetch updated questions and render partial HTML
        questions = Question.objects.filter(user=request.user, delflag=False).order_by('id')
        html = render_to_string("partials/question_rows.html", {"questions": questions, "user": request.user,
            "user_role": request.user.role,       # ← add this
            "show_edit_button": False}, request=request)
        return JsonResponse({"message": "Questions uploaded successfully!", "html": html})

    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


# ------------------------------
# Add Single Question
# ------------------------------
from decimal import Decimal, InvalidOperation

@jwt_required
@role_required('staff')
@require_http_methods(["GET", "POST"])
def add_question(request):
    if request.method == "GET":
        categories = Category.objects.filter(delflag=False)
        subjects = Subject.objects.filter(delflag=False)
        sets = Set.objects.filter(user=request.user, delflag=False)
        questions = Question.objects.filter(user=request.user, delflag=False)
        return render(request, "questions/add_questions.html", {
            "categories": categories,
            "subjects": subjects,
            "sets": sets,
            "questions": questions,
            "user_role": request.user.role,
            "user": request.user,
            "show_edit_button": True,
        })

    # POST request
    data = request.POST
    question_text = data.get("question_text", "").strip()
    option_a = data.get("option_a", "").strip()
    option_b = data.get("option_b", "").strip()
    option_c = data.get("option_c", "").strip()
    option_d = data.get("option_d", "").strip()
    correct_option = data.get("correct_option", "").strip().upper()
    subject_id = data.get("subject")
    set_id = data.get("set")  # Single set
    difficulty_score = data.get("difficulty_score", "").strip()  # New field

    # Validate required fields
    if not all([question_text, option_a, option_b, option_c, option_d, correct_option, subject_id, set_id, difficulty_score]):
        return JsonResponse({"message": "All fields are required."}, status=400)

    # Validate difficulty_score is a decimal within range
    try:
        difficulty_score = Decimal(difficulty_score)
        if not (Decimal('0.10') <= difficulty_score <= Decimal('0.90')):
            return JsonResponse({"message": "Difficulty must be between 0.10 and 0.90."}, status=400)
    except InvalidOperation:
        return JsonResponse({"message": "Invalid difficulty value."}, status=400)

    # Fetch related objects
    subject = get_object_or_404(Subject, id=subject_id, delflag=False)
    set_obj = get_object_or_404(Set, id=set_id, user=request.user, delflag=False)

    # Create the question
    Question.objects.create(
        subject=subject,
        set=set_obj,
        user=request.user,
        question_text=question_text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_option=correct_option,
        difficulty_score=difficulty_score
    )

    # Fetch updated questions and render partial HTML
        # After creating the question
    questions = Question.objects.filter(user=request.user, delflag=False).order_by('id')
    html = render_to_string(
        "partials/question_rows.html",
        {
            "questions": questions,
            "user": request.user,
            "user_role": request.user.role,       # ← add this
            "show_edit_button": True              # ← add this
        },
        request=request
    )
    return JsonResponse({"message": "Question added successfully!", "html": html})


# ------------------------------
# List Questions
# ------------------------------
@jwt_required
@role_required('staff')
def question_list(request):
    questions = Question.objects.filter(delflag=False).order_by('id')
    return render(request, "questions/questions_list.html", {"questions": questions, "user_role": request.user.role, "user": request.user})


# --# ------------------------------
# Edit Question
# ------------------------------

@jwt_required
@role_required('staff')
@require_POST
def edit_question(request, pk):
    question = get_object_or_404(Question, id=pk, delflag=False)
    data = request.POST

    # Get form data
    question_text = data.get("question_text", "").strip()
    option_a = data.get("option_a", "").strip()
    option_b = data.get("option_b", "").strip()
    option_c = data.get("option_c", "").strip()
    option_d = data.get("option_d", "").strip()
    correct_option = data.get("correct_option", "").strip().upper()
    subject_id = data.get("subject")
    set_id = data.get("set")  # Single set
    difficulty_score = data.get("difficulty_score", "").strip()  # New field

    if not all([question_text, option_a, option_b, option_c, option_d, correct_option, subject_id, set_id, difficulty_score]):
        return JsonResponse({"message": "All fields are required."}, status=400)

    # Validate difficulty_score
    try:
        difficulty_score = Decimal(difficulty_score)
        if not (Decimal('0.10') <= difficulty_score <= Decimal('0.90')):
            return JsonResponse({"message": "Difficulty must be between 0.10 and 0.90."}, status=400)
    except (InvalidOperation, TypeError):
        return JsonResponse({"message": "Invalid difficulty value."}, status=400)

    # Fetch related objects
    subject = get_object_or_404(Subject, id=subject_id, delflag=False)
    set_obj = get_object_or_404(Set, id=set_id, user=request.user, delflag=False)

    # Update question
    question.subject = subject
    question.set = set_obj
    question.question_text = question_text
    question.option_a = option_a
    question.option_b = option_b
    question.option_c = option_c
    question.option_d = option_d
    question.correct_option = correct_option
    question.difficulty_score = difficulty_score  # Update difficulty
    question.save()

    # Render updated questions list
    questions = Question.objects.filter(user=request.user, delflag=False).order_by('id')
    html = render_to_string(
    "partials/question_rows.html",
    {
        "questions": questions,
        "user": request.user,
        "user_role": request.user.role,
        "show_edit_button": True
    },
    request=request
    )


    return JsonResponse({"message": "Question updated successfully!", "html": html})


@jwt_required
@role_required('staff')
def get_question_rows(request):
    questions = Question.objects.filter(user=request.user, delflag=False).order_by('id')
    html = render_to_string(
        "partials/question_rows.html",
        {
            "questions": questions,
            "user": request.user,
            "user_role": request.user.role,
            "show_edit_button": True
        },
        request=request
    )
    return JsonResponse({"html": html})

# ------------------------------
# Delete / Restore / Recycle Bin
# ------------------------------
@csrf_exempt
@jwt_required
@role_required('staff')
@require_POST
def delete_question(request, pk):
    question = get_object_or_404(Question, id=pk, delflag=False)
    question.delflag = True
    question.save()

    questions = Question.objects.filter(user=request.user, delflag=False).order_by('id')
    html = render_to_string(
        "partials/question_rows.html", 
        {
            "questions": questions, 
            "user": request.user,
            "user_role": request.user.role,  # ✅ Already passed here
            "show_edit_button": True
        },
        request=request
    )
    
    return JsonResponse({"message": "Question deleted successfully!", "html": html})



@jwt_required
@role_required('staff')
def question_recycle_bin(request):
    deleted_questions = Question.objects.filter(delflag=True)
    return render(request, "questions/recycle_bin.html", {"deleted_questions": deleted_questions, "user": request.user})


@jwt_required
@role_required('staff')
@require_POST
def restore_question(request, pk):
    question = get_object_or_404(Question, pk=pk, delflag=True)
    question.delflag = False
    question.save()
    return JsonResponse({"message": "Question restored successfully."})


@jwt_required
@role_required('staff')
def get_subjects_by_category(request, category_id):
    subjects = Subject.objects.filter(category_id=category_id, delflag=False).values("id", "name")
    return JsonResponse({"subjects": list(subjects)})


@jwt_required
@role_required('staff')
def get_sets_by_category(request, category_id):
    
    sets = Set.objects.filter(category_id=category_id, user=request.user, delflag=False).values("id", "name")
    return JsonResponse({"sets": list(sets)})


from django.shortcuts import render, get_object_or_404
# from .models import Set

# @jwt_required
# @role_required("student")
# def start_test(request, slug):
#     test_set = get_object_or_404(Set, slug=slug)
#     return render(request, "questions/start_test.html", {"set": test_set})


# @jwt_required
# @role_required("student")
# def get_result(request, attempt_id):
#     attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
#     answers = attempt.answers.select_related("question__subject")

#     total = answers.count()
#     correct = answers.filter(is_correct=True).count()
#     wrong = answers.filter(is_answered=True, is_correct=False).count()
#     not_answered = answers.filter(is_answered=False).count()

#     # Subject-wise wrong (count unanswered as wrong too)
#     wrong_by_subject = (
#         answers.filter(Q(is_correct=False) | Q(is_answered=False))
#         .values("question__subject__name")
#         .annotate(count=Count("id"))
#         .order_by("-count")
#     )

#     return JsonResponse({
#         "total": total,
#         "correct": correct,
#         "wrong": wrong,
#         "not_answered": not_answered,
#         "wrong_by_subject": list(wrong_by_subject),
#     })

# @jwt_required
# @role_required("student")
# @require_POST
# def submit_answer(request):
#     question_id = request.POST.get("question_id")
#     selected_option = request.POST.get("selected_option", "")
#     attempt_id = request.POST.get("attempt_id")

#     attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
#     question = get_object_or_404(Question, id=question_id)

#     correct = (selected_option == question.correct_option)
#     is_answered = bool(selected_option)

#     UserAnswer.objects.update_or_create(
#         attempt=attempt,
#         question=question,
#         defaults={
#             "selected_option": selected_option,
#             "is_correct": correct,
#             "is_answered": is_answered,
#         }
#     )

#     # Move pointer
#     attempt.current_index += 1
#     attempt.save()

#     return JsonResponse({
#         "question": question.question_text,
#         "correct_option": question.correct_option,
#         "selected": selected_option,
#         "is_correct": correct
#     })

# @jwt_required
# @role_required("student")
# def get_question(request):
#     set_id = request.GET.get("set_id")
#     attempt_id = request.GET.get("attempt_id")

#     attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user, test_set_id=set_id)

#     # Fetch all questions for this set in a fixed order
#     questions = list(Question.objects.filter(set_id=set_id, delflag=False).order_by("id"))
    
#     if attempt.current_index >= len(questions):
#         attempt.completed = True
#         attempt.save()
#         return JsonResponse({"status": "completed"})

#     question = questions[attempt.current_index]

#     return JsonResponse({
#         "status": "ongoing",
#         "question_id": question.id,
#         "text": question.question_text,
#         "options": {
#             "A": question.option_a,
#             "B": question.option_b,
#             "C": question.option_c,
#             "D": question.option_d
#         }
#     })

# from django.utils import timezone
# from .models import Attempt, UserAnswer

# @jwt_required
# @role_required("student")
# def assign_random_set(request):
#     subject_id = request.GET.get("subject_id")
#     set_obj = Set.objects.filter(subject_id=subject_id, delflag=False).order_by("?").first()

#     if not set_obj:
#         return JsonResponse({"status": "error", "message": "No set found for this subject."})

#     # Check if an incomplete attempt exists
#     attempt, created = Attempt.objects.get_or_create(
#         user=request.user,
#         test_set=set_obj,
#         completed=False
#     )

#     return JsonResponse({
#         "status": "success",
#         "set_id": set_obj.id,
#         "attempt_id": attempt.id
#     })

# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from django.utils import timezone
# from .models import Attempt, UserAnswer, Question, Set

# # # ------------------ START TEST ------------------
# # def start_test(request, set_id):
# #     """Start or resume a test attempt"""
# #     user = request.user
# #     test_set = get_object_or_404(Set, id=set_id)

# #     # resume unfinished attempt
# #     attempt = Attempt.objects.filter(user=user, set=test_set, completed_at__isnull=True).first()
# #     if not attempt:
# #         attempt = Attempt.objects.create(user=user, set=test_set)

# #     # fetch first unanswered question
# #     answered_qs = UserAnswer.objects.filter(attempt=attempt).values_list('question_id', flat=True)
# #     question = Question.objects.filter(set=test_set, delflag=False).exclude(id__in=answered_qs).first()

# #     if not question:
# #         return JsonResponse({"done": True, "message": "Test already completed."})

# #     return JsonResponse({
# #         "attempt_id": attempt.id,
# #         "question": {
# #             "id": question.id,
# #             "text": question.question_text,
# #             "options": {
# #                 "A": question.option_a,
# #                 "B": question.option_b,
# #                 "C": question.option_c,
# #                 "D": question.option_d,
# #             }
# #         },
# #         "current": answered_qs.count() + 1,
# #         "total": Question.objects.filter(set=test_set, delflag=False).count(),
# #         "time_limit": 30,
# #     })

# from django.utils import timezone
# from django.http import JsonResponse

# @jwt_required
# @role_required("student")
# def init_attempt(request, slug):
#     """Create or resume an attempt and return attempt_id"""
#     test_set = get_object_or_404(Set, slug=slug)
#     user = request.user

#     # Resume unfinished attempt
#     attempt = Attempt.objects.filter(user=user, set=test_set, completed_at__isnull=True).first()
#     if not attempt:
#         attempt = Attempt.objects.create(
#             user=user,
#             set=test_set,
#             current_difficulty=0.50,   # default start
#             current_index=0
#         )

#     return JsonResponse({
#         "attempt_id": attempt.id,
#         "set": test_set.name,
#         "current_difficulty": str(attempt.current_difficulty),
#     })


# # ------------------ NEXT QUESTION ------------------
# def next_question(request, attempt_id):
#     """Load the next unanswered question"""
#     user = request.user
#     attempt = get_object_or_404(Attempt, id=attempt_id, user=user)
#     test_set = attempt.set

#     answered_qs = UserAnswer.objects.filter(attempt=attempt).values_list("question_id", flat=True)
#     question = Question.objects.filter(set=test_set, delflag=False).exclude(id__in=answered_qs).first()

#     if not question:
#         attempt.completed_at = timezone.now()
#         attempt.save()
#         return JsonResponse({"done": True})

#     return JsonResponse({
#         "question": {
#             "id": question.id,
#             "text": question.question_text,
#             "options": {
#                 "A": question.option_a,
#                 "B": question.option_b,
#                 "C": question.option_c,
#                 "D": question.option_d,
#             }
#         },
#         "current": answered_qs.count() + 1,
#         "total": Question.objects.filter(set=test_set, delflag=False).count(),
#         "time_limit": 30,
#     })


# # ------------------ REVIEW ATTEMPT ------------------
# def review_attempt(request, attempt_id):
#     """Final review after completion"""
#     attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
#     answers = UserAnswer.objects.filter(attempt=attempt).select_related("question")

#     data = {
#         "total": answers.count(),
#         "correct": answers.filter(is_correct=True).count(),
#         "answers": [
#             {
#                 "question": ans.question.question_text,
#                 "selected_option": ans.selected_option,
#                 "is_answered": bool(ans.selected_option),
#                 "is_correct": ans.is_correct,
#             }
#             for ans in answers
#         ]
#     }
#     return JsonResponse(data)

# from django.db.models import F
# from django.db.models.functions import Abs
# def get_question(request):
#     set_id = request.GET.get("set_id")
#     attempt_id = request.GET.get("attempt_id")

#     attempt = get_object_or_404(Attempt, id=attempt_id, set_id=set_id, user=request.user)

#     # ✅ Select next question based on current difficulty
#     question = Question.objects.filter(
#         set_id=set_id,
#         difficulty_score=attempt.current_difficulty,
#         delflag=False
#     ).exclude(
#         id__in=attempt.answers.values_list("question_id", flat=True)
#     ).order_by('?').first()

#     if not question:
#         attempt.completed = True
#         attempt.completed_at = timezone.now()
#         attempt.save()
#         return JsonResponse({"status": "completed"})

#     return JsonResponse({
#         "status": "ok",
#         "question_id": question.id,
#         "text": question.question_text,
#         "options": {
#             "A": question.option_a,
#             "B": question.option_b,
#             "C": question.option_c,
#             "D": question.option_d,
#         },
#         "difficulty": str(question.difficulty_score)  # ✅ send difficulty to frontend
#     })

# from django.utils import timezone
# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# def submit_answer(request):
#     qid = request.POST.get("question_id")
#     attempt_id = request.POST.get("attempt_id")
#     selected_option = request.POST.get("selected_option")

#     attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
#     question = get_object_or_404(Question, id=qid)

#     is_correct = None
#     is_answered = False

#     if selected_option:  # answered
#         is_correct = (selected_option == question.correct_option)
#         is_answered = True

#     # ✅ Save answer
#     UserAnswer.objects.create(
#         user=request.user,
#         attempt=attempt,
#         question=question,
#         selected_option=selected_option if selected_option else None,
#         is_correct=is_correct,
#         is_answered=is_answered,
#     )

#     # ✅ Adaptive difficulty logic
#     if is_correct:
#         attempt.current_difficulty = min(1.00, attempt.current_difficulty + 0.10)  # move up
#     else:
#         attempt.current_difficulty = max(0.10, attempt.current_difficulty - 0.10)  # move down

#     attempt.current_index += 1
#     attempt.save()

#     return JsonResponse({
#         "question": question.question_text,
#         "correct_option": question.correct_option,
#         "is_correct": is_correct,
#     })
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count
from question_sets.models import Set
from questions.models import Question, Attempt, UserAnswer

# from accounts.decorators import jwt_required, role_required

@jwt_required
@role_required("student")
def start_test(request, slug):
    test_set = get_object_or_404(Set, slug=slug, delflag=False)

    # Use the correct reverse name from related_name='questions'
    questions_qs = test_set.questions.filter(delflag=False)

    count = questions_qs.count()
    # seconds per question = total seconds / number of questions
    per_q_time = (test_set.duration_minutes * 60 // count) if count else 0

    return render(request, "questions/start_test.html", {
        "set": test_set,
        "per_q_time": per_q_time,     # seconds per question
        "total_duration": test_set.duration_minutes,  # whole set duration in minutes
    })


from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
# from .models import Attempt, Set
# from .decorators import jwt_required, role_required


@jwt_required
@role_required("student")
def init_attempt(request, slug):
    """Start a new attempt or resume unfinished one"""
    
    test_set = get_object_or_404(Set, slug=slug)

    attempt, created = Attempt.objects.get_or_create(
        user=request.user,
        set=test_set,  # ✅ use correct field name
        completed=False,
        defaults={"started_at": timezone.now()}  # ✅ match your model field
    )

    return JsonResponse({
        "status": "success",
        "set_id": test_set.id,
        "attempt_id": attempt.id,
        "message": "Attempt started" if created else "Resuming your test"
    })

from django.db.models import F
from django.db.models.functions import Abs
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import F
from django.db.models.functions import Abs

@jwt_required
@role_required("student")
def get_question(request):
    """Return the next question (adaptive by difficulty)"""
    set_id = request.GET.get("set_id")
    attempt_id = request.GET.get("attempt_id")

    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    test_set = get_object_or_404(Set, id=set_id)

    # answered questions so far
    answered_ids = UserAnswer.objects.filter(
        attempt=attempt
    ).values_list("question_id", flat=True)

    # remaining questions
    remaining = Question.objects.filter(set=test_set, delflag=False).exclude(id__in=answered_ids)
    if not remaining.exists():
        attempt.completed = True
        attempt.completed_at = timezone.now()
        attempt.save()
        return JsonResponse({"status": "completed"})

    # adaptive difficulty
    last_answer = UserAnswer.objects.filter(attempt=attempt).order_by("-id").first()
    if last_answer:
        if last_answer.is_correct:
            target_diff = min(last_answer.question.difficulty_score + Decimal('0.10'), Decimal('1.00'))
        else:
            target_diff = max(last_answer.question.difficulty_score - Decimal('0.10'), Decimal('0.10'))
    else:
        target_diff = Decimal('0.50')

    # find nearest question by difficulty
    question = remaining.annotate(
        diff=Abs(F("difficulty_score") - target_diff)
    ).order_by("diff").first()

    return JsonResponse({
        "status": "ok",
        "question_id": question.id,
        "text": question.question_text,  # ensure your model field is question_text
        "difficulty": float(question.difficulty_score),
        "options": {
            "A": question.option_a,
            "B": question.option_b,
            "C": question.option_c,
            "D": question.option_d,
        }
    })


from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

@jwt_required
@role_required("student")
def submit_answer(request):
    qid = request.POST.get("question_id")
    attempt_id = request.POST.get("attempt_id")
    selected_option = request.POST.get("selected_option")

    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    question = get_object_or_404(Question, id=qid)

    is_correct = None
    is_answered = False

    if selected_option:  # answered
        is_correct = (selected_option == question.correct_option)
        is_answered = True

    # Save answer with user populated
    UserAnswer.objects.create(
        user=request.user,
        attempt=attempt,
        question=question,
        selected_option=selected_option if selected_option else None,
        is_correct=is_correct,
        is_answered=is_answered,
    )

    # Adaptive difficulty using Decimal
    if is_correct:
        attempt.current_difficulty = min(Decimal('1.00'), attempt.current_difficulty + Decimal('0.10'))
    else:
        attempt.current_difficulty = max(Decimal('0.10'), attempt.current_difficulty - Decimal('0.10'))

    attempt.current_index += 1
    attempt.save()

    return JsonResponse({
        "question": question.question_text,  # or question.text if your field is named text
        "correct_option": question.correct_option,
        "is_correct": is_correct,
    })

from django.db.models import Count
from django.db.models import Q, Count

@jwt_required
@role_required("student")
def result(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)

    answers = UserAnswer.objects.filter(attempt=attempt)
    total = answers.count()
    correct = answers.filter(is_correct=True).count()
    wrong = answers.filter(is_correct=False).count()
    not_answered = answers.filter(is_answered=False).count()  # ✅ use is_answered

    wrong_by_subject = (
        answers.filter(Q(is_correct=False) | Q(is_answered=False))
        .values("question__subject__name")
        .annotate(count=Count("id"))
    )

    return JsonResponse({
        "status": "ok",
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "not_answered": not_answered,
        "wrong_by_subject": list(wrong_by_subject),
    })


@jwt_required
@role_required("student")
def review_attempt(request, attempt_id):
    """Render review page for student"""
    attempt = get_object_or_404(Attempt, id=attempt_id, student=request.user)
    answers = UserAnswer.objects.filter(attempt=attempt).select_related("question")

    return render(request, "questions/review_attempt.html", {
        "attempt": attempt,
        "answers": answers,
    })




# def suggest_books_for_subject(request):
#     subject_name = request.GET.get('subject', '')
#     books = []

#     if subject_name:
#         # Fetch books directly from Gemini AI
#         ai_books = get_books_from_ai(subject_name)
#         for b in ai_books:
#             # Save to DB if not already present
#             book, created = Book.objects.get_or_create(
#                 title=b["title"],
#                 subject=subject_name,
#                 defaults={
#                     "price": b["price"],
#                     "rating": b["rating"],
#                     "description": b["description"]
#                 }
#             )
#             books.append(book)

#     return render(request, 'partials/book_table.html', {'books': books})
from django.shortcuts import render, get_object_or_404
from questions.models import Book
from django.http import HttpResponse
from .utils import get_books_from_ai
import re
# from .utils import get_books_from_ai

@jwt_required
@role_required("student")
def suggest_books_for_subject(request):
    subject_name = request.GET.get('subject', '').strip()
    books = []

    if subject_name:
        ai_books = get_books_from_ai(subject_name)

        for b in ai_books:
            try:
                # Always sanitize price before saving
                raw_price = str(b.get("price", 0))
                clean_price = re.sub(r'[^\d.]', '', raw_price)  # remove $ ₹ or text
                inr_price = float(clean_price) if clean_price else 0.0
            except Exception:
                inr_price = 0.0

            book, created = Book.objects.get_or_create(
                title=b["title"],
                subject=subject_name,
                defaults={
                    "price": inr_price,  # stored clean INR number
                    "rating": b.get("rating", 0),
                    "description": b.get("description", "")
                }
            )
            books.append(book)

    return render(request, 'partials/book_table.html', {'books': books})

# # utils.py
# import json
# from google import genai
# from django.conf import settings

# def get_books_from_ai(subject_name, max_books=5):
#     """
#     Fetch book suggestions from Gemini AI based on the subject.
#     Returns a list of dictionaries:
#     [{"title": ..., "price": ..., "rating": ..., "description": ...}, ...]
#     """
#     client = genai.Client(api_key=settings.GEMINI_API_KEY)

#     prompt = f"""
#     Suggest {max_books} books for the subject "{subject_name}".
#     For each book, provide: title, price in USD, rating (out of 5), and a short description.
#     Return the answer as a JSON array.
#     """

#     try:
#         response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=prompt
#         )
#         # Convert JSON string to Python list
#         books = json.loads(response.text)
#         # Ensure books is a list of dicts
#         if not isinstance(books, list):
#             raise ValueError("AI response is not a JSON list")
#     except Exception as e:
#         print(f"Error fetching books from AI: {e}")
#         books = []  # Return empty list instead of dummy data

#     return books
from django.shortcuts import render
from django.http import HttpResponse
from questions.models import Book

@jwt_required
@role_required("student")
def book_suggestions_page(request):
    subjects = request.GET.getlist("subjects")  # multiple weakest subjects
    subject_books = {}

    for subject_name in subjects:
        books = suggest_books_for_subject_logic(subject_name)  # extract logic into helper
        # Render partial for each subject
        table_html = render(request, "partials/book_table.html", {"books": books}).content.decode("utf-8")
        subject_books[subject_name] = table_html

    return render(request, "questions/suggestions.html", {"subject_books": subject_books})


# helper function (reuse your existing suggest_books_for_subject logic without request)
def suggest_books_for_subject_logic(subject_name):
    books = []
    if subject_name:
        ai_books = get_books_from_ai(subject_name)
        for b in ai_books:
            try:
                price_str = str(b["price"]).replace("$", "").strip()
                usd_price = float(price_str)
                inr_price = round(usd_price * 80, 2)
            except Exception:
                inr_price = 0.0

            book, created = Book.objects.get_or_create(
                title=b["title"],
                subject=subject_name,
                defaults={
                    "price": inr_price,
                    "rating": b["rating"],
                    "description": b["description"]
                }
            )
            books.append(book)
    return books
