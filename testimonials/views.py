from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import PublicTestimonialForm


def submit_testimonial(request):
    if request.method == "POST":
        form = PublicTestimonialForm(request.POST)

        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.is_approved = False
            testimonial.is_featured = False
            testimonial.save()

            messages.success(
                request,
                "Thank you for sharing your experience. "
                "Your review has been submitted for clinic approval."
            )
            return redirect("testimonials:submit_testimonial")
    else:
        form = PublicTestimonialForm()

    return render(request, "testimonials/submit.html", {
        "form": form,
    })
