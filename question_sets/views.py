import re
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods, require_POST

from account.decorators import jwt_required, role_required
from .models import Set
from category.models import Category
from subject.models import Subject


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
            "sets": sets,                # ✅ add this
            "user_role": request.user.role,  # ✅ add this
            "user": request.user,        # ✅ add this
        })

    # ----------------------
    # POST (add new set)
    # ----------------------
    category_id = request.POST.get("category")
    set_name = request.POST.get("set_name")

    if set_name and not re.fullmatch(r"[A-Z]+(_[A-Z]+)*", set_name):
        return JsonResponse({"message": "Set name must be in CAPITAL letters, underscores (_) allowed."}, status=400)

    if set_name and category_id:
        try:
            category = Category.objects.get(id=category_id, delflag=False)

            # Reactivate if soft-deleted set exists
            soft_deleted = Set.objects.filter(name=set_name, category=category, delflag=True).first()
            if soft_deleted:
                soft_deleted.delflag = False
                soft_deleted.user = request.user
                soft_deleted.save()
            else:
                if Set.objects.filter(name=set_name, category=category, delflag=False).exists():
                    return JsonResponse({"message": "Set already exists for this category."}, status=400)

                Set.objects.create(
                    name=set_name,
                    category=category,
                    user=request.user,
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

    if set_name and not re.fullmatch(r"[A-Z]+(_[A-Z]+)*", set_name):
        return JsonResponse({"message": "Set name must be in CAPITAL letters, underscores (_) allowed."}, status=400)

    if set_name and category_id:
        try:
            category = Category.objects.get(id=category_id, delflag=False)

            if Set.objects.filter(name=set_name, category=category, delflag=False).exclude(id=set_obj.id).exists():
                return JsonResponse({"message": "Set already exists for this category."}, status=400)

            set_obj.name = set_name
            set_obj.category = category
            set_obj.save()

            sets = Set.objects.select_related("category", "user").filter(delflag=False)
            html = render_to_string("partials/set_rows.html", {"sets": sets, "user_role": request.user.role}, request=request)

            return JsonResponse({"message": "Set updated successfully!", "html": html})

        except Category.DoesNotExist:
            return JsonResponse({"message": "Invalid category."}, status=400)

    return JsonResponse({"message": "All fields are required."}, status=400)

from questions.models import Question
# -------------------------------
# Delete Set (Soft Delete)
# @jwt_required
@role_required("staff")
@require_POST
def delete_set(request, pk):
    set_obj = get_object_or_404(Set, pk=pk, delflag=False)

    # Permission check
    if set_obj.user != request.user:
        return JsonResponse({"message": "Unauthorized: You can only delete your own sets."}, status=403)

    # Soft-delete the set
    set_obj.delflag = True
    set_obj.save()

    # Soft-delete all related questions
    Question.objects.filter(set=set_obj, delflag=False).update(delflag=True)

    # Return updated active sets
    sets = Set.objects.select_related("category", "user").filter(delflag=False)
    set_data = [
        {"id": s.id, "name": s.name, "category_id": s.category.id, "category_name": s.category.name}
        for s in sets
    ]

    return JsonResponse({"message": "Set and its related questions deleted successfully.", "sets": set_data})

# -------------------------------
# Recycle Bin (Deleted Sets)
# -------------------------------
@jwt_required
@role_required("staff")
def set_recycle_bin(request):
    sets = Set.objects.select_related("category", "user").filter(delflag=True, user=request.user)
    return render(request, "question_sets/recycle_bin.html", {"sets": sets})


# -------------------------------
# Restore Set
# -------------------------------
@jwt_required
@role_required("staff")
@require_POST
def restore_set(request, pk):
    # Get the soft-deleted set
    set_obj = get_object_or_404(Set, pk=pk, delflag=True)

    # Permission check
    if set_obj.user != request.user:
        return JsonResponse({"message": "Unauthorized: You can only restore your own sets."}, status=403)

    # Restore the set
    set_obj.delflag = False
    set_obj.save()

    # Restore all related questions that were soft-deleted
    Question.objects.filter(set=set_obj, delflag=True).update(delflag=False)

    return JsonResponse({"message": "Set and its related questions restored successfully."})




# views.py
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

@jwt_required
@role_required("staff")
def get_set_rows(request):
    sets = Set.objects.select_related("category", "user").filter(delflag=False).order_by("id")
    html = render_to_string("partials/set_rows.html", {
        "sets": sets,   # pass queryset
        "user_role": request.user.role,
        "user": request.user
    })
    print("DEBUG HTML:", html)  # should show <tr> rows now
    return JsonResponse({"html": html})





