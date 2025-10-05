from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.db.models import Sum, Q
from django.http import FileResponse
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
import io
import os
import xlwt
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db import models
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from django.contrib.auth.decorators import login_required
from .decorators import group_required
from .models import Doctor, Patient , Medicine , Supplier, LabExamination, LabExaminationItem, Appointment, Prescription,PrescriptionItem,Invoice
from .forms import DoctorForm, PatientForm, MedicineForm, SupplierForm, LabExaminationForm, LabExaminationItemFormSet, PrescriptionForm, PrescriptionItemForm,AppointmentForm, InvoiceForm,PrescriptionItemFormSet
from django.forms import modelformset_factory


# ======================== AUTHENTICATION VIEWS ========================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('redirect_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"ښه راغلاست, {user.first_name} {user.last_name}!")
                next_url = request.GET.get('next', 'redirect_dashboard')
                return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('redirect_dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='auth/password_reset_email.html',
                subject_template_name='auth/password_reset_subject.txt'
            )
            messages.success(request, "Password reset instructions sent to your email.")
            return redirect('login')
        else:
            messages.error(request, "Please enter a valid email address.")
    else:
        form = PasswordResetForm()

    return render(request, 'auth/password_reset.html', {'form': form})


# ======================== SEARCH ALL ========================

def search_all(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.filter(
        Q(full_name__icontains=query) | Q(contact__icontains=query)
    )
    doctors = Doctor.objects.filter(
        Q(full_name__icontains=query) | Q(specialization__icontains=query) | Q(contact__icontains=query)
    )
    medicines = Medicine.objects.filter(
        Q(name__icontains=query) | Q(supplier__name__icontains=query) | Q(generic_name__icontains=query) | Q(batch_no__icontains=query)
    )
    suppliers = Supplier.objects.filter(
        Q(name__icontains=query) | Q(contact__icontains=query) | Q(email__icontains=query)
    )
    lab_examinations = LabExamination.objects.filter(
        Q(doctor__full_name__icontains=query) | Q(patient__full_name__icontains=query)
    )
    prescriptions = Prescription.objects.filter(
        Q(patient__full_name__icontains=query) | Q(doctor__full_name__icontains=query)
    )
    invoices = Invoice.objects.filter(
        Q(patient__full_name__icontains=query)
    )

    context = {
        'query': query,
        'patients': patients,
        'doctors': doctors,
        'medicines': medicines,
        'suppliers': suppliers,
        'lab_examinations': lab_examinations,
        'prescriptions': prescriptions,
        'invoices': invoices
    }
    return render(request, 'search_results.html', context)


@login_required
def redirect_dashboard(request):
    user = request.user
    if user.groups.filter(name='Admin').exists():
        return redirect('admin_dashboard')
    elif user.groups.filter(name='Reception').exists():
        return redirect('reception_dashboard')
    elif user.groups.filter(name='Doctor').exists():
        return redirect('doctor_dashboard')
    elif user.groups.filter(name='Lab Rant').exists():
        return redirect('lab_dashboard')
    elif user.groups.filter(name='Pharmacist').exists():
        return redirect('pharmacist_dashboard')
    elif user.groups.filter(name='Finance').exists():
        return redirect('finance_dashboard')
    else:
        return redirect('login')  # default


@group_required('Admin')
def admin_dashboard(request):
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    suppliers = Supplier.objects.all()
    medicines = Medicine.objects.all()
    invoices = Invoice.objects.all()
    labs = LabExamination.objects.all()
    appointments=Appointment.objects.all()
    prescriptions = Prescription.objects.all()
    context= {
        'appointments':appointments,
        'prescriptions':prescriptions,
        'labs':labs,'invoices':invoices,
        'doctors': doctors, 
        'patients': patients,
        'suppliers':suppliers,
        'medicines':medicines}
    return render(request, 'dashboards/admin.html',context )

@group_required('Reception')
def reception_dashboard(request):
    return render(request, 'dashboards/reception.html')



# <======================================Doctor========================================>
@group_required('Doctor')
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)  # Assuming doctor is logged in

    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    total_patients = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()
    total_prescriptions = Prescription.objects.filter(doctor=doctor).count()

    context = {
        'doctor': doctor,
        'total_appointments': total_appointments,
        'total_patients': total_patients,
        'total_prescriptions': total_prescriptions,
    }
    return render(request, 'doctor/dashboard.html', context)

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctor/doctor_list.html', {'doctors': doctors})

def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    appointments = Appointment.objects.filter(doctor=doctor)
    prescriptions = Prescription.objects.filter(doctor=doctor)
    lab_exams = LabExamination.objects.filter(doctor=doctor)

    context = {
        'doctor': doctor,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'lab_exams': lab_exams,
        
    }
    return render(request, 'doctor/detail.html', context)


def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.save()
            messages.success(request, 'Record Inserted Successfully !')
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'doctor/doctor_form.html', {'form': form})

def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, instance=doctor)
    if form.is_valid():
        form.save()
        messages.success(request, "Doctor updated successfully.")
        return redirect('doctor_list')
    return render(request, 'doctor/doctor_form.html', {'form': form})

def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, "Doctor deleted.")
        return redirect('doctor_list')
    return render(request, 'doctor/doctor_confirm_delete.html', {'doctor': doctor})


# <======================================Patient========================================>
def patient_detail_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    appointments = Appointment.objects.filter(patient=patient)
    lab_exam = LabExamination.objects.filter(patient=patient)
    prescription = Prescription.objects.filter(patient=patient)
    invoices = Invoice.objects.filter(patient=patient)

    context = {
        'patient': patient,
        'appointments': appointments,
        'lab_exam': lab_exam,
        'prescription': prescription,
        'invoices': invoices,
    }
    return render(request, 'patient/patient_detail.html', context)

def patient_list(request):
    patients = Patient.objects.all().order_by('-registration_date','-id')
    return render(request, 'patient/patient_list.html', {'patients': patients})

def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.save()
            messages.success(request, 'Record Inserted Successfully !')
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'patient/patient_form.html', {'form': form})

def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if form.is_valid():
        form.save()
        messages.success(request, "Patient updated successfully.")
        return redirect('patient_list')
    return render(request, 'patient/patient_form.html', {'form': form})

def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, "Patient deleted.")
        return redirect('patient_list')
    return render(request, 'patient/patient_confirm_delete.html', {'patient': patient})



# <======================================Medicine========================================>

def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'medicine/medicine_list.html', {'medicines': medicines})

def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    prescriptions = PrescriptionItem.objects.filter(medicine=medicine)
    total_prescribed = prescriptions.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_sales = total_prescribed * medicine.selling_price
    is_expired = medicine.expiry_date < timezone.now().date()

    context = {
        'medicine': medicine,
        'prescriptions': prescriptions,
        'total_prescribed': total_prescribed,
        'total_sales': total_sales,
        'is_expired': is_expired,
    }
    return render(request, 'medicine/detail.html', context)

def restock_medicine(request, pk):
    medicine = Medicine.objects.get(pk=pk)
    if request.method == "POST":
        qty = int(request.POST.get("quantity", 0))
        medicine.quantity += qty
        medicine.save()
        messages.success(request, f"{medicine.name} restocked by {qty}.")
        return redirect("medicine_detail", pk=medicine.id)
    return render(request, "pharmacy/restock_form.html", {"medicine": medicine})



def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.save()
            messages.success(request, 'Record Inserted Successfully !')
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'medicine/medicine_form.html', {'form': form})

def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, instance=medicine)
    if form.is_valid():
        form.save()
        messages.success(request, "Medicine updated successfully.")
        return redirect('medicine_list')
    return render(request, 'medicine/medicine_form.html', {'form': form})

def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, "Medicine deleted.")
        return redirect('medicine_list')
    return render(request, 'medicine/medicine_confirm_delete.html', {'medicine': medicine})

# <======================================Supplier========================================>
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'supplier/supplier_list.html', {'suppliers': suppliers})

def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'supplier/detail.html', {'supplier': supplier})


def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.save()
            messages.success(request, 'Record Inserted Successfully !')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'supplier/supplier_form.html', {'form': form})

def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=supplier)
    if form.is_valid():
        form.save()
        messages.success(request, "Supplier updated successfully.")
        return redirect('supplier_list')
    return render(request, 'supplier/supplier_form.html', {'form': form})

def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, "Supplier deleted.")
        return redirect('supplier_list')
    return render(request, 'supplier/supplier_confirm_delete.html', {'supplier': supplier})

# <======================================LabEximination========================================>

def lab_dashboard(request):
    # --- Date Range Filter ---
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    exams = LabExamination.objects.all()

    if start_date and end_date:
        exams = exams.filter(date__range=[start_date, end_date])

    # --- Stats ---
    total_exams = exams.count()
    total_income = (
        LabExaminationItem.objects.filter(lab_exam__in=exams).aggregate(Sum("price"))["price__sum"] or 0
    )
    completed_exams = exams.filter(items__result__isnull=False).distinct().count()
    pending_exams = total_exams - completed_exams

    # --- Recent Exams ---
    recent_exams = exams.order_by("-date")[:5]

    # --- Chart Data (last 7 days) ---
    last_7_days = [now().date() - timedelta(days=i) for i in range(6, -1, -1)]
    exam_counts = [exams.filter(date=day).count() for day in last_7_days]

    context = {
        "total_exams": total_exams,
        "pending_exams": pending_exams,
        "completed_exams": completed_exams,
        "total_income": total_income,
        "recent_exams": recent_exams,
        "chart_labels": [d.strftime("%b %d") for d in last_7_days],
        "chart_data": exam_counts,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "dashboards/lab.html", context)

def lab_list(request):
    lab_exams = LabExamination.objects.select_related("patient", "doctor").all()
    return render(request, "lab/lab_list.html", {"lab_exams": lab_exams})

# Detail of a single lab examination (with items)
def lab_detail(request, pk):
    lab_exam = get_object_or_404(LabExamination, pk=pk)
    items = lab_exam.items.all()  # related_name="items" from LabExaminationItem
    return render(request, "lab/detail.html", {
        "lab_exam": lab_exam,
        "items": items
    })

def lab_create(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")

        # Create main LabExamination
        lab_exam = LabExamination.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id if doctor_id else None
        )

        # Create items from POST data
        exam_types = request.POST.getlist("examination_type[]")
        prices = request.POST.getlist("price[]")
        results = request.POST.getlist("result[]")

        for exam_type, price, result in zip(exam_types, prices, results):
            if exam_type.strip():  # skip empty rows
                LabExaminationItem.objects.create(
                    lab_exam=lab_exam,
                    examination_type=exam_type,
                    price=price or 0,
                    result=result
                )

        return redirect("lab_detail", pk=lab_exam.pk)

    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    return render(request, "lab/lab_form.html", {
        "patients": patients,
        "doctors": doctors,
    })


def lab_update(request, pk):
    lab_exam = get_object_or_404(LabExamination, pk=pk)
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    lab_items = LabExaminationItem.objects.filter(lab_exam=lab_exam)

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        date = request.POST.get("date")

        # Update main fields
        lab_exam.patient_id = patient_id
        lab_exam.doctor_id = doctor_id
        lab_exam.date = date
        lab_exam.save()

        # Delete old items
        lab_items.delete()

        # Add updated lab items
        exam_types = request.POST.getlist("examination_type[]")
        prices = request.POST.getlist("price[]")
        results = request.POST.getlist("result[]")

        for exam_type, price, result in zip(exam_types, prices, results):
            if exam_type.strip():  # Only save if type is provided
                LabExaminationItem.objects.create(
                    lab_exam=lab_exam,
                    examination_type=exam_type,
                    price=price or 0,
                    result=result or ""
                )

        return redirect("lab_detail", pk=lab_exam.pk)

    return render(request, "lab/lab_form.html", {
        "lab_exam": lab_exam,
        "items": lab_items,   # 👈 this makes them available in the template
        "patients": patients,
        "doctors": doctors,
    })

def lab_delete(request, pk):
    lab_exam = get_object_or_404(LabExamination, pk=pk)
    patient_id = lab_exam.patient.id  # Save patient ID for redirect

    if request.method == "POST":
        lab_exam.delete()  # Will also delete related LabExaminationItem (cascade)
        return redirect("lab_list")

    return render(request, "lab/lab_confirm_delete.html", {
        "lab_exam": lab_exam
    })



# <======================================Appointment========================================>
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-appointment_date','-id')
    return render(request, 'appointment/appointment_list.html', {'appointments': appointments})

def appointment_create(request):
    form = AppointmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_form.html', {'form': form})

def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if form.is_valid():
        form.save()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_form.html', {'form': form})

def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_confirm_delete.html', {'appointment': appointment})


# <======================================Prescription========================================>
def prescription_list(request):
    prescriptions = Prescription.objects.all().order_by("-date")
    return render(request, "prescription/prescription_list.html", {
        "prescriptions": prescriptions
    })

def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    return render(request, "prescription/prescription_detail.html", {
        "prescription": prescription
    })

def prescription_create(request):
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    medicines = Medicine.objects.all()

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        diagnosis = request.POST.get("diagnosis")
        regimen = request.POST.get("regimen")

        prescription = Prescription.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            diagnosis=diagnosis,
            regimen=regimen
        )

        medicine_ids = request.POST.getlist("medicine[]")
        dosages = request.POST.getlist("dosage[]")
        quantities = request.POST.getlist("quantity[]")

        for med_id, dosage, qty in zip(medicine_ids, dosages, quantities):
            if med_id and qty:
                PrescriptionItem.objects.create(
                    prescription=prescription,
                    medicine_id=med_id,
                    dosage=dosage,
                    quantity=int(qty)
                )

        return redirect("prescription_detail", pk=prescription.pk)

    return render(request, "prescription/prescription_form.html", {
        "patients": patients,
        "doctors": doctors,
        "medicines": medicines
    })


def prescription_edit(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    medicines = Medicine.objects.all()
    prescription_items = PrescriptionItem.objects.filter(prescription=prescription)

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        diagnosis = request.POST.get("diagnosis")
        regimen = request.POST.get("regimen")

        # Update prescription main fields
        prescription.patient_id = patient_id
        prescription.doctor_id = doctor_id
        prescription.diagnosis = diagnosis
        prescription.regimen = regimen
        prescription.save()

        # Delete existing items first
        prescription_items.delete()

        # Add updated medicine items
        medicine_ids = request.POST.getlist("medicine[]")
        dosages = request.POST.getlist("dosage[]")
        quantities = request.POST.getlist("quantity[]")

        for med_id, dosage, qty in zip(medicine_ids, dosages, quantities):
            if med_id and qty:
                PrescriptionItem.objects.create(
                    prescription=prescription,
                    medicine_id=med_id,
                    dosage=dosage,
                    quantity=int(qty)
                )

        return redirect("prescription_detail", pk=prescription.pk)

    return render(request, "prescription/prescription_form.html", {
        "prescription": prescription,
        "prescription_items": prescription_items,
        "patients": patients,
        "doctors": doctors,
        "medicines": medicines
    })



def prescription_delete(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    if request.method == "POST":
        prescription.delete()  # each item’s delete() will restock
        messages.success(request, "Prescription deleted ✅")
        return redirect("prescription_list")
    return render(request, "prescription/prescription_confirm_delete.html", {
        "prescription": prescription
    })

   



# <======================================Invoice========================================>
def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'invoice/invoice_list.html', {'invoices': invoices})

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, "invoice/detail.html", {
        "invoice": invoice
    })

def invoice_create(request):
    form = InvoiceForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('invoice_list')
    return render(request, 'invoice/invoice_form.html', {'form': form})

def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = InvoiceForm(request.POST or None, instance=invoice)
    if form.is_valid():
        form.save()
        return redirect('invoice_list')
    return render(request, 'invoice/invoice_form.html', {'form': form})

def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('invoice_list')
    return render(request, 'invoice/invoice_confirm_delete.html', {'invoice': invoice})




# @group_required('Lab Rant')
# def lab_dashboard(request):
#     return render(request, 'dashboards/lab.html')

@group_required('Pharmacist')
def pharmacist_dashboard(request):
    return render(request, 'dashboards/pharmacist.html')

@group_required('Finance')
def finance_dashboard(request):
    return render(request, 'dashboards/finance.html')




