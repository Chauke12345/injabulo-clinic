from django import forms
from .models import CorporateEnquiry


class CorporateEnquiryForm(forms.ModelForm):
    class Meta:
        model = CorporateEnquiry
        fields = [
            "company_name",
            "industry",
            "contact_person",
            "email",
            "phone",
            "employee_count",
            "service_type",
            "preferred_date",
            "service_location",
            "additional_requirements",
        ]

        widgets = {
            "company_name": forms.TextInput(attrs={
                "placeholder": "Enter your company name",
            }),
            "industry": forms.TextInput(attrs={
                "placeholder": "e.g. Mining, Education, Manufacturing",
            }),
            "contact_person": forms.TextInput(attrs={
                "placeholder": "Full name of contact person",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "company@example.com",
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Company contact number",
            }),
            "employee_count": forms.NumberInput(attrs={
                "min": "1",
                "placeholder": "Estimated number of employees",
            }),
            "preferred_date": forms.DateInput(attrs={
                "type": "date",
            }),
            "service_location": forms.TextInput(attrs={
                "placeholder": "Where should the service take place?",
            }),
            "additional_requirements": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Tell us about your company's healthcare requirements...",
            }),
        }

    def clean_employee_count(self):
        count = self.cleaned_data["employee_count"]
        if count < 1:
            raise forms.ValidationError("Employee count must be at least 1.")
        return count


from .models import CorporateQuotation, CorporateQuotationItem


class CorporateQuotationForm(forms.ModelForm):
    class Meta:
        model = CorporateQuotation
        fields = [
            "enquiry",
            "issue_date",
            "valid_until",
            "status",
            "notes",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "valid_until": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Additional quotation terms and conditions...",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get("issue_date")
        valid_until = cleaned_data.get("valid_until")

        if issue_date and valid_until and valid_until < issue_date:
            self.add_error(
                "valid_until",
                "The validity date cannot be earlier than the issue date."
            )

        return cleaned_data


class CorporateQuotationItemForm(forms.ModelForm):
    class Meta:
        model = CorporateQuotationItem
        fields = ["description", "quantity", "unit_price"]
        widgets = {
            "description": forms.TextInput(attrs={
                "placeholder": "e.g. Employee medical assessment",
            }),
            "quantity": forms.NumberInput(attrs={"min": "1"}),
            "unit_price": forms.NumberInput(attrs={
                "min": "0.01",
                "step": "0.01",
            }),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity

    def clean_unit_price(self):
        price = self.cleaned_data["unit_price"]
        if price <= 0:
            raise forms.ValidationError("Unit price must be greater than zero.")
        return price
