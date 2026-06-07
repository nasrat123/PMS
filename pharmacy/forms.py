from django import forms
from .models import Doctor, Patient , Medicine , Supplier, LabExamination, BirthRegistration, Expense, Employee, Department, LabExaminationItem, Appointment, Prescription,PrescriptionItem, Invoice, Donor, BloodDonation, BloodRequest, BloodGroup, BloodStock
from ckeditor.widgets import CKEditorWidget
from django.forms.models import inlineformset_factory, modelformset_factory
from datetime import date

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'
        widgets = {
            'photo':forms.ClearableFileInput(attrs={'class':'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={"class": "form-control"}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'available_days': forms.TextInput(attrs={'class': 'form-control'}),
            'address': CKEditorWidget(),
            'experience': CKEditorWidget(),
            'education': CKEditorWidget(),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={"class": "form-control"}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'join_date': forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
        }


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={"class": "form-control"}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'sick_type': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_date': forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
        }

class BloodGroupForm(forms.ModelForm):
    class Meta:
        model = BloodGroup
        fields = '__all__'
        widgets = {
            'name': forms.Select(attrs={"class": "form-control"}),
        }


class BloodStockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = '__all__'
        widgets = {
            'blood_group': forms.Select(attrs={"class": "form-control"}),
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={"class": "form-control"}),
            'blood_group': forms.Select(attrs={"class": "form-control"}),
            'last_donation_date': forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
        }


class BloodDonationForm(forms.ModelForm):
    class Meta:
        model = BloodDonation
        fields = '__all__'
        widgets = {
            'units': forms.TextInput(attrs={'class': 'form-control'}),
            'donor': forms.Select(attrs={"class": "form-control"}),
            'blood_group': forms.Select(attrs={"class": "form-control"}),
            'donation_date': forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
        }


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = '__all__'
        widgets = {
            'units_required': forms.TextInput(attrs={'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={"class": "form-control"}),
            'status': forms.Select(attrs={"class": "form-control"}),
            'doctor': forms.Select(attrs={"class": "form-control"}),
            'blood_group': forms.Select(attrs={"class": "form-control"}),
            'request_date': forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'issued_date': forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
        }





class BirthRegistrationForm(forms.ModelForm):
    class Meta:
        model = BirthRegistration
        fields = '__all__'
        widgets = {
            'baby_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_type': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'mother': forms.Select(attrs={'class': 'form-control'}),
            'weight_kg': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={"class": "form-control"}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control'}),
            'time_of_birth': forms.TimeInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mother'].queryset = Patient.objects.filter(gender='F')    


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'generic_name', 'supplier', 'batch_no', 'expiry_date', 'quantity', 'purchase_price', 'selling_price', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'batch_no': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_price': forms.TextInput(attrs={'class': 'form-control'}),
            'selling_price': forms.TextInput(attrs={'class': 'form-control'}),
            'description': CKEditorWidget(),
            'expiry_date': forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
        }




class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact', 'email', 'address', 'about']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'about': CKEditorWidget(),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'status', 'about']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'about': CKEditorWidget(),
        }


# -------------------------------
# Main Lab Examination form
# -------------------------------
class LabExaminationForm(forms.ModelForm):
    class Meta:
        model = LabExamination
        fields = ["patient", "doctor", "date"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-control"}),
            "doctor": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

# -------------------------------
# Lab Examination Item form
# -------------------------------
class LabExaminationItemForm(forms.ModelForm):
    class Meta:
        model = LabExaminationItem
        fields = ["examination_type", "result", "price", "unit", "normal"]
        widgets = {
            "examination_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "Examination Type"}),
            "unit":  forms.TextInput(attrs={"class": "form-control", "placeholder": " Unit"}),
            "normal":  forms.TextInput(attrs={"class": "form-control", "placeholder": " Normal Rang"}),
            "result":  forms.TextInput(attrs={"class": "form-control", "placeholder": " Result"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Price"}),
        }

# -------------------------------
# Formset for multiple items
# -------------------------------
LabExaminationItemFormSet = inlineformset_factory(
    parent_model=LabExamination,
    model=LabExaminationItem,
    form=LabExaminationItemForm,
    extra=1,        # 0 by default; we'll use empty_form as template
    can_delete=True
)





class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'
        widgets = {
            "patient": forms.Select(attrs={"class": "form-control"}),
            "doctor": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "appointment_date": forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control', "placeholder": "YYYY/MM/DD HH:MM:SS"
                },
                format='%Y-%m-%d'
            ),
        }




class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["patient", "doctor", "diagnosis", "regimen"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-control"}),
            "doctor": forms.Select(attrs={"class": "form-control"}),
            "diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "regimen": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ["medicine", "quantity", "dosage"]
        widgets = {
            "medicine": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "dosage": forms.TextInput(attrs={"class": "form-control"}),
        }

PrescriptionItemFormSet = inlineformset_factory(
    parent_model=Prescription,
    model=PrescriptionItem,
    form=PrescriptionItemForm,
    extra=1,
    can_delete=True
)



class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'
        widgets = {
            "patient": forms.Select(attrs={"class": "form-control"}),
            "service_type": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "narrative": forms.TextInput(attrs={'class': 'form-control'}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "date": forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control', "placeholder": "YYYY/MM/DD"
                },
                format='%Y-%m-%d'
            ),
        }



class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = '__all__'
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={'class': 'form-control'}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "date": forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date picker
                    'class': 'form-control', "placeholder": "YYYY/MM/DD"
                },
                format='%Y-%m-%d'
            ),
        }