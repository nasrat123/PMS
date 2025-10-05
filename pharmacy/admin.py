from django.contrib import admin
from .models import (
    Patient,
    Doctor,
    Supplier,
    Medicine,
    LabExamination,
    Appointment,
    Prescription,
    PrescriptionItem,
    Invoice,
    LabExaminationItem
)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'gender', 'contact', 'registration_date')
    search_fields = ('full_name', 'contact')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'education', 'experience', 'specialization', 'contact', 'available_days')
    search_fields = ('user__username', 'specialization')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'address')
    search_fields = ('name',)

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'supplier', 'quantity', 'batch_no', 'description', 'purchase_price', 'quantity', 'selling_price' , 'expiry_date')
    list_filter = ('supplier', 'expiry_date')
    search_fields = ('name', 'generic_name',)

class LabExaminationItemInline(admin.TabularInline):
    model = LabExaminationItem
    extra = 0

@admin.register(LabExamination)
class LabExaminationAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "get_examination_types", "date", "total_cost")
    list_filter = ("date", "patient", "doctor")  # use only real fields
    inlines = [LabExaminationItemInline]

    def get_examination_types(self, obj):
        return ", ".join([item.examination_type for item in obj.items.all()])
    get_examination_types.short_description = "Examination Types"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__full_name', 'doctor__user__username')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date')
    search_fields = ('patient__full_name',)

@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'medicine', 'dosage')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'amount', 'service_type', 'status')
    list_filter = ('status', 'service_type')
    search_fields = ('patient__full_name',)
