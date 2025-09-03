import re
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods, require_POST

from account.decorators import jwt_required, role_required
from .models import Set
from category.models import Category
from subject.models import Subject
from questions.models import Question


# -------------------------------
# List Active Sets
# -------------------------------
@jwt_required
@role_required("staff")
def set_list(request):
    sets = Set.objects.select_related("category", "user").filter(delflag=False)
    categories = Category.objects.filter(delflag=False)
    return render(request, "set/set_list.html", {
        "sets": sets,
        "categories": categories,
        "user_role": request.user.role,
    })


# -------------------------------
# Add Set
# -------------------------------

@jwt_required
@role_required("staff")
@require_http_methods(["GET", "POST"])
def add_set(request):
    if request.method == "GET":
        categories = Category.objects.filter(delflag=False)
        sets = Set.objects.select_related("category", "user").filter(delflag=False).order_by("id")
        return render(request, "question_sets/add_set.html", {
            "categories": categories,
            "sets": sets,
            "user_role": request.user.role,
            "user": request.user,
        })

    # ----------------------
    # POST (add new set)
    # ----------------------
    category_id = request.POST.get("category")
    set_name = request.POST.get("set_name")
    duration = request.POST.get("duration_minutes", "").strip()


    if set_name and not re.fullmatch(r"[A-Z]+(_[A-Z]+)*", set_name):
        return JsonResponse({"message": "Set name must be in CAPITAL letters, underscores (_) allowed."}, status=400)

    if not duration or not duration.isdigit() or int(duration) <= 0:
        return JsonResponse({"message": "Duration must be a positive number (in minutes)."}, status=400)

    if set_name and category_id:
        try:
            category = Category.objects.get(id=category_id, delflag=False)

            # Reactivate if soft-deleted set exists
            soft_deleted = Set.objects.filter(name=set_name, category=category, delflag=True).first()
            if soft_deleted:
                soft_deleted.delflag = False
                soft_deleted.user = request.user
                soft_deleted.duration = duration  # ✅ update
                soft_deleted.save()
            else:
                if Set.objects.filter(name=set_name, category=category, delflag=False).exists():
                    return JsonResponse({"message": "Set already exists for this category."}, status=400)

                Set.objects.create(
                    name=set_name,
                    category=category,
                    user=request.user,
                    duration_minutes=duration,  # ✅ correct field name
                )


            # ✅ Reload rows after saving
            sets = Set.objects.select_related("category", "user").filter(delflag=False).order_by("id")
            html = render_to_string("partials/set_rows.html", {
                "sets": sets,
                "user_role": request.user.role,
                "user": request.user
            })

            return JsonResponse({"message": "Set added successfully!", "html": html})

        except Category.DoesNotExist:
            return JsonResponse({"message": "Invalid category."}, status=400)

    return JsonResponse({"message": "All fields are required."}, status=400)


# -------------------------------
# Edit Set
# -------------------------------
@jwt_required
@role_required("staff")
@require_POST
def edit_set(request, pk):
    set_obj = get_object_or_404(Set, pk=pk, delflag=False)

    if set_obj.user != request.user:
        return JsonResponse({"message": "Unauthorized: You can only edit your own sets."}, status=403)

    set_name = request.POST.get("set_name")
    category_id = request.POST.get("category")
    duration = request.POST.get("duration_minutes", "").strip()  # ✅ match add_set

    # Validate set name format
    if set_name and not re.fullmatch(r"[A-Z]+(_[A-Z]+)*", set_name):
        return JsonResponse({"message": "Set name must be in CAPITAL letters, underscores (_) allowed."}, status=400)

    # Validate duration
    if not duration or not duration.isdigit() or int(duration) <= 0:
        return JsonResponse({"message": "Duration must be a positive number (in minutes)."}, status=400)

    if set_name and category_id:
        try:
            category = Category.objects.get(id=category_id, delflag=False)

            # Check for duplicates in the same category
            if Set.objects.filter(name=set_name, category=category, delflag=False).exclude(id=set_obj.id).exists():
                return JsonResponse({"message": "Set already exists for this category."}, status=400)

            # ✅ Update set
            set_obj.name = set_name
            set_obj.category = category
            set_obj.duration_minutes = duration   # ✅ match model field
            set_obj.save()

            # Reload rows
            sets = Set.objects.select_related("category", "user").filter(delflag=False)
            html = render_to_string("partials/set_rows.html", {
                "sets": sets,
                "user_role": request.user.role,
                "user": request.user
            }, request=request)

            return JsonResponse({"message": "Set updated successfully!", "html": html})

        except Category.DoesNotExist:
            return JsonResponse({"message": "Invalid category."}, status=400)

    return JsonResponse({"message": "All fields are required."}, status=400)


# -------------------------------
# Delete Set (Soft Delete)
# ----from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string

# -------------------------------
# Delete Set (Soft Delete)
# -------------------------------
@jwt_required
@role_required("staff")
@require_POST
def delete_set(request, pk):
    set_obj = get_object_or_404(Set, pk=pk, delflag=False)

    # Permission check
    if set_obj.user != request.user:
        return JsonResponse(
            {"message": "Unauthorized: You can only delete your own sets."},
            status=403
        )

    # Soft-delete the set
    set_obj.delflag = True
    set_obj.save()

    # Soft-delete all related questions
    Question.objects.filter(set=set_obj, delflag=False).update(delflag=True)

    # Return updated active sets
    sets = Set.objects.filter(user=request.user, delflag=False).select_related("category", "user")
    html = render_to_string("partials/set_rows.html", {"sets": sets}, request=request)

    return JsonResponse({
        "message": "Set and its related questions deleted successfully.",
        "html": html
    })


# -------------------------------
# Recycle Bin (Deleted Sets)
# -------------------------------
@jwt_required
@role_required("staff")
def set_recycle_bin(request):
    sets = Set.objects.filter(delflag=True, user=request.user).select_related("category", "user")
    return render(request, "question_sets/recycle_bin.html", {"sets": sets})


# -------------------------------
# Restore Set
# -------------------------------
@jwt_required
@role_required("staff")
@require_POST
def restore_set(request, pk):
    set_obj = get_object_or_404(Set, pk=pk, delflag=True)

    if set_obj.user != request.user:
        return JsonResponse(
            {"message": "Unauthorized: You can only restore your own sets."},
            status=403
        )

    # Restore set
    set_obj.delflag = False
    set_obj.save()

    # Restore related questions
    Question.objects.filter(set=set_obj, delflag=True).update(delflag=False)

    # Return updated active sets
    sets = Set.objects.filter(user=request.user, delflag=False).select_related("category", "user")
    html = render_to_string("partials/set_rows.html", {"sets": sets}, request=request)

    return JsonResponse({
        "message": "Set and its related questions restored successfully.",
        "html": html
    })


# -------------------------------
# Reload Active Set Rows
# -------------------------------
@jwt_required
@role_required("staff")
def get_set_rows(request):
    sets = Set.objects.select_related("category", "user").filter(delflag=False).order_by("id")
    html = render_to_string("partials/set_rows.html", {
        "sets": sets,
        "user_role": request.user.role,
        "user": request.user
    })
    return JsonResponse({"html": html})
