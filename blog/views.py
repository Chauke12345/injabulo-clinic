from django.shortcuts import render, get_object_or_404
from .models import BlogPost, BlogCategory


def post_list(request, category_slug=None):
    posts = BlogPost.objects.filter(is_published=True).select_related("category")
    categories = BlogCategory.objects.filter(posts__is_published=True).distinct()

    selected_category = None

    if category_slug:
        selected_category = get_object_or_404(
            BlogCategory,
            slug=category_slug
        )
        posts = posts.filter(category=selected_category)

    return render(request, "blog/post_list.html", {
        "posts": posts,
        "categories": categories,
        "selected_category": selected_category,
    })


def post_detail(request, slug):
    post = get_object_or_404(
        BlogPost.objects.select_related("category"),
        slug=slug,
        is_published=True
    )

    return render(request, "blog/post_detail.html", {
        "post": post,
    })
