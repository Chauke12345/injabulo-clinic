from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CorporateEnquiryForm


def corporate_wellness(request):
    if request.method == "POST":
        form = CorporateEnquiryForm(request.POST)

        if form.is_valid():
            enquiry = form.save()

            messages.success(
                request,
                "Thank you! Your corporate wellness enquiry has been "
                "received. Our team will contact you."
            )
            return redirect("corporate:corporate_wellness")
    else:
        form = CorporateEnquiryForm()

    return render(request, "corporate/corporate_wellness.html", {
        "form": form,
    })
