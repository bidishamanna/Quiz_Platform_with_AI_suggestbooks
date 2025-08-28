import re
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods, require_POST

from category.models import Category
from .models import Subject
from account.decorators import jwt_required, role_required


# -------------------------------
# Add Subject (GET + POST)
# -------------------------------
@jwt_required
@role_required('staff')
@require_http_methods(["GET", "POST"])
def add_subject(request):
    if request.method == "GET":
        categories = Category.objects.filter(delflag=False)
        subjects = Subject.objects.select_related("category").filter(delflag=False)
        return render(request, "subject/add_subject.html", {
            "categories": categories,
            "subjects": subjects,
            "user_role": request.user.role,
        })

    category_id = request.POST.get("category")
    subject_name = request.POST.get("subject_name")

    if subject_name and not re.fullmatch(r"[A-Z]+(_[A-Z]+)*", subject_name):
        return JsonResponse({
            "message": "Subject name must contain only capital letters (A–Z), with optional underscores (_)."
        }, status=400)

    if subject_name and category_id:
        try:
            category = Category.objects.get(id=category_id, delflag=False)

            # Reactivate soft-deleted subject if exists
            soft_deleted = Subject.objects.filter(name=subject_name, category=category, delflag=True).first()
            if soft_deleted:
                soft_deleted.delflag = False
                soft_deleted.user = request.user
                soft_deleted.save()
            else:
                if Subject.objects.filter(name=subject_name, category=category, delflag=False).exists():
                    return JsonResponse({"message": "Subject already exists for this category."}, status=400)

                Subject.objects.create(
                    name=subject_name,
                    category=category,
                    user=request.user,
                )

            subjects = Subject.objects.select_related("category").filter(delflag=False)
            html = render_to_string("partials/subject_rows.html", {
                "subjects": subjects,
                "user_role": request.user.role,
                "user": request.user,
            })

            return JsonResponse({"message": "Subject added successfully!", "html": html})

        except Category.DoesNotExist:
            return JsonResponse({"message": "Selected category does not exist or is deleted."}, status=400)

    return JsonResponse({"message": "All fields are required."}, status=400)


# -------------------------------
# Edit Subject
# -------------------------------
@jwt_required
@role_required('staff')
@require_POST
def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk, delflag=False)

    if subject.user != request.user:
        return JsonResponse({"message": "Unauthorized. You can only edit your own subject."}, status=403)

    subject_name = request.POST.get("subject_name")
    category_id = request.POST.get("category")

    if subject_name and not re.fullmatch(r"[A-Z]+(_[A-Z]+)*", subject_name):
        return JsonResponse({
            "message": "Subject name must contain only capital letters (A–Z), with optional underscores (_)."
        }, status=400)

    if subject_name and category_id:
        try:
            category = Category.objects.get(id=category_id, delflag=False)

            if Subject.objects.filter(
                name=subject_name, category=category, delflag=False
            ).exclude(id=subject.id).exists():
                return JsonResponse({"message": "Subject with this name already exists in the selected category."}, status=400)

            subject.name = subject_name
            subject.category = category
            subject.save()

            subjects = Subject.objects.select_related("category").filter(delflag=False)
            html = render_to_string(
                "partials/subject_rows.html",
                {"subjects": subjects, "user_role": request.user.role, "user": request.user},
                request=request
            )

            return JsonResponse({"message": "Subject updated successfully!", "html": html})

        except Category.DoesNotExist:
            return JsonResponse({"message": "Selected category not found."}, status=400)

    return JsonResponse({"message": "All fields are required."}, status=400)

from questions.models import Question
# -------------------------------
# Delete Subject (Soft Delete)
# -------------------------------
@jwt_required
@role_required('staff')
@require_POST
def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk, delflag=False)

    if subject.user != request.user:
        return JsonResponse({"message": "Unauthorized. You can only delete your own subject."}, status=403)

    # Soft-delete the subject
    subject.delflag = True
    subject.save()

    # Soft-delete all related questions
    Question.objects.filter(subject=subject, delflag=False).update(delflag=True)

    # Return updated active subjects
    subjects = Subject.objects.select_related("category").filter(delflag=False)
    subject_data = [
        {"id": s.id, "name": s.name, "category_id": s.category.id, "category_name": s.category.name}
        for s in subjects
    ]
    return JsonResponse({"message": "Subject and related questions deleted successfully.", "subjects": subject_data})


# -------------------------------
# Subject Recycle Bin (View Deleted)
# -------------------------------

@jwt_required
@role_required('staff')
def subject_recycle_bin(request):
    subjects = Subject.objects.select_related("category").filter(delflag=True, user=request.user)
    return render(request, "subject/recycle_bin.html", {"subjects": subjects})


# -------------------------------
# Restore Subject
# -------------------------------
@jwt_required
@role_required('staff')
@require_POST
def restore_subject(request, pk):
    # Get the soft-deleted subject
    subject = get_object_or_404(Subject, pk=pk, delflag=True)

    # Permission check
    if subject.user != request.user:
        return JsonResponse({"message": "You do not have permission to restore this subject."}, status=403)

    # Restore the subject
    subject.delflag = False
    subject.save()

    # Restore all related questions that were soft-deleted
    Question.objects.filter(subject=subject, delflag=True).update(delflag=False)

    return JsonResponse({"message": "Subject and its related questions restored successfully."})


# -------------------------------
# Subject List (Active Only)
# -------------------------------
@jwt_required
@role_required('staff')
def subject_list(request):
    subjects = Subject.objects.select_related("category").filter(delflag=False)
    return render(request, "subject/subject_list.html", {"subjects": subjects})


# -------------------------------
# Load Subjects by Category (AJAX)
# -------------------------------
@jwt_required
@role_required('staff')
def get_subject_rows(request):
    subjects = Subject.objects.select_related("category").filter(delflag=False).order_by('id')  # newest at bottom
    html = render_to_string("partials/subject_rows.html", {
        "subjects": subjects,
        "user_role": request.user.role,
        "user": request.user,
    })
    return JsonResponse({"html": html})
