from django import forms
from .models import Doctor, Patient , Medicine , Supplier, LabExamination, LabExaminationItem, Appointment, Prescription,PrescriptionItem,Invoice
from ckeditor.widgets import CKEditorWidget
from django.forms.models import inlineformset_factory, modelformset_factory

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
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



class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['full_name', 'age', 'gender', 'contact', 'address', 'sick_type', 'registration_date']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
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
        fields = ["examination_type", "result", "price"]
        widgets = {
            "examination_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "Examination Type"}),
            "result": CKEditorWidget(),
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
