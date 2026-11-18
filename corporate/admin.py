from django.contrib import admin
from .models import CorporateEnquiry, CorporateQuotation, CorporateQuotationItem


class CorporateQuotationItemInline(admin.TabularInline):
    model = CorporateQuotationItem
    extra = 1


@admin.register(CorporateEnquiry)
class CorporateEnquiryAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_person", "service_type", "status", "created_at")
    list_filter = ("status", "service_type")
    search_fields = ("company_name", "contact_person", "email", "phone")


@admin.register(CorporateQuotation)
class CorporateQuotationAdmin(admin.ModelAdmin):
    list_display = ("reference", "enquiry", "issue_date", "valid_until", "status", "subtotal")
    list_filter = ("status", "issue_date")
    search_fields = ("reference", "enquiry__company_name")
    inlines = [CorporateQuotationItemInline]
    readonly_fields = ("created_at", "updated_at")
