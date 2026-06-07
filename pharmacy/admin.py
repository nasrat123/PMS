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
    LabExaminationItem,
    Expense,
    Employee,
    Department,
    BloodGroup,
    BloodStock,
    Donor, 
    BloodDonation, 
    BloodRequest,
    BirthRegistration
)


@admin.register(BloodGroup)
class BloodGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'quantity')

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'blood_group', 'phone', 'last_donation_date')
    search_fields = ('full_name', 'phone')

@admin.register(BloodDonation)
class BloodDonationAdmin(admin.ModelAdmin):
    list_display = ('donor','blood_group','units','donation_date')
    search_fields = ('donor__full_name',)
    date_hierarchy = 'donation_date'

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('patient','blood_group','units_required','status','request_date')
    list_filter = ('status','blood_group')
    search_fields = ('patient__full_name',)


@admin.register(BirthRegistration)
class BirthRegistrationAdmin(admin.ModelAdmin):
    list_display = ('baby_name','date_of_birth','time_of_birth','mother','doctor','delivery_type')
    search_fields = ('baby_name','mother__full_name','father_name')
    date_hierarchy = 'date_of_birth'

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name','status')
    search_fields = ('name',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'gender', 'contact', 'registration_date')
    search_fields = ('full_name', 'contact')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'gender','photo', 'contact', 'join_date')
    search_fields = ('full_name', 'contact')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'photo', 'education', 'experience', 'specialization', 'contact', 'available_days')
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


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'date', 'added_by', 'created_at')
    list_filter = ('category', 'date')
    search_fields = ('title', 'description')
