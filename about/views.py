from django.shortcuts import render


from django.shortcuts import render,redirect
from category.models import Category
from subject.models import Subject
from django.shortcuts import render
from category.models import Category
from subject.models import Subject


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from category.models import Category
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from question_sets.models import Set

def home(request):
    categories = Category.objects.filter(delflag=False)
    return render(request, 'about/home.html', {'categories': categories})


from django.shortcuts import render, get_object_or_404
# from .models import Category, Set
from django.http import JsonResponse

# def get_sets(request, category_slug):
#     # Fetch category by slug (not deleted)
#     category = get_object_or_404(Category, slug=category_slug, delflag=False)
    
#     # Fetch sets belonging to the category (not deleted)
#     sets = Set.objects.filter(category=category, delflag=False).values("id", "name")
    
#     if not sets:
#         return JsonResponse({"message": "No sets found for this category."}, status=404)
    
#     return JsonResponse(list(sets), safe=False)

def category_sets_page(request, category_slug):
    # Fetch category by slug (not deleted)
    category = get_object_or_404(Category, slug=category_slug, delflag=False)
    
    # Fetch sets belonging to the category (not deleted)
    sets = Set.objects.filter(category=category, delflag=False)
    
    return render(request, 'about/category_sets_page.html', {'category': category, 'sets': sets})

# from django.shortcuts import render, get_object_or_404
# # from .models import Category, Set

# def category_view(request, category_id):
#     # Fetch category by ID (not deleted)
#     category = get_object_or_404(Category, id=category_id, delflag=False)
    
#     # Fetch sets belonging to the category (not deleted)
#     sets = Set.objects.filter(category=category, delflag=False)
    
#     return render(request, 'about/category_view.html', {'category': category, 'sets': sets})

def contact(request):
    return render(request,'about/contact.html')

def about(request):
    return render(request,'about/about.html')

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from questions.models import UserAnswer, Attempt
from account.models import User
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Q
# from .models import UserAnswer
from django.db.models import Count, Q, Subquery, OuterRef


def home_leaderboard_view(request):
    """
    Returns the highest scorer from each set (username, score, category, set).
    - Only considers the LATEST attempt per student.
    - Skips sets with no attempts or 0 score.
    """
    leaderboard = []

    for quiz_set in Set.objects.all():
        # Latest attempt for each user in this set
        latest_attempt = (
            Attempt.objects.filter(set=quiz_set, user=OuterRef("user"))
            .order_by("-started_at")
        )

        # Calculate score from latest attempt
        scores = (
            UserAnswer.objects.filter(attempt=Subquery(latest_attempt.values("id")[:1]))
            .filter(is_correct=True)
            .values(
                "user__username",
                "attempt__set__name",
                "attempt__set__category__name",
            )
            .annotate(score=Count("id"))
            .order_by("-score")
        )

        # Pick the top scorer (highest score > 0)
        top_player = next((s for s in scores if s["score"] > 0), None)

        if top_player:
            leaderboard.append(top_player)

    # ✅ AJAX → return JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"leaderboard": leaderboard})

    # ✅ Normal page render
    return render(request, "home_leaderboard.html", {"leaderboard": leaderboard})
