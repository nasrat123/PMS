from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F
PAGINATE_BY = 20
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, Border, Side
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta, datetime, date
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
import io
import os
import xlwt
from django.contrib.staticfiles import finders
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.db import models
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from .decorators import group_required
from .models import BloodGroup, BloodStock, Donor,BirthRegistration, BloodDonation, BloodRequest, Doctor, Patient , Medicine , Department, Employee, Supplier, Expense, LabExamination, LabExaminationItem, Appointment, Prescription,PrescriptionItem,Invoice
from .forms import DonorForm, BloodDonationForm,BirthRegistrationForm, BloodGroupForm, BloodRequestForm, DoctorForm, PatientForm, MedicineForm, ExpenseForm, DepartmentForm, EmployeeForm, SupplierForm, LabExaminationForm, LabExaminationItemFormSet, PrescriptionForm, PrescriptionItemForm,AppointmentForm, InvoiceForm,PrescriptionItemFormSet
from django.forms import modelformset_factory



def get_filtered_expenses_from_request(request):
    """
    Return queryset filtered exactly like expense_list view based on GET params.
    """
    qs = Expense.objects.all().order_by('-date')

    search = request.GET.get('search') or request.GET.get('q')
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if search:
        qs = qs.filter(title__icontains=search)
    if category:
        qs = qs.filter(category=category)
    if start_date:
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d").date()
            qs = qs.filter(date__gte=sd)
        except Exception:
            pass
    if end_date:
        try:
            ed = datetime.strptime(end_date, "%Y-%m-%d").date()
            qs = qs.filter(date__lte=ed)
        except Exception:
            pass

    return qs


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
@login_required
def profile_view(request):
    user = request.user
    group_name = user.groups.first().name if user.groups.exists() else "No Role"

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            user.save()
            messages.success(request, "Profile updated successfully!")

        elif 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not check_password(current_password, user.password):
                messages.error(request, "Current password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # keep user logged in
                messages.success(request, "Password changed successfully!")

        return redirect('profile_view')

    context = {
        'user': user,
        'group_name': group_name,
    }
    return render(request, 'profile.html', context)


# ======================== SEARCH ALL ========================
@login_required
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
        return render(request, 'newuser.html')


@group_required('Admin')
def admin_dashboard(request):
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    suppliers = Supplier.objects.all()
    medicines = Medicine.objects.all()
    invoices = Invoice.objects.all()
    labs = LabExamination.objects.all()
    appointments=Appointment.objects.all()
    employees=Employee.objects.all()
    births=BirthRegistration.objects.all()
    bloods=BloodStock.objects.all()
    departments=Department.objects.all()
    prescriptions = Prescription.objects.all()
    context= {
        'bloods':bloods,
        'births':births,
        'employees':employees,
        'departments':departments,
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
    # Summary stats
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(
        appointment_date__date=date.today()
    ).count()

    # Monthly appointment stats
    current_year = datetime.now().year
    monthly_data = (
        Appointment.objects.filter(appointment_date__year=current_year)
        .values_list('appointment_date__month')
        .annotate(count=Count('id'))
    )
    months = list(range(1, 13))
    appointment_counts = [dict(monthly_data).get(m, 0) for m in months]

    # Recent appointments
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-appointment_date')[:10]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'months': months,
        'appointment_counts': appointment_counts,
        'recent_appointments': recent_appointments,
    }

    return render(request, 'dashboards/reception.html', context)


# <======================================Birht========================================>
class BirthFilterableListView(LoginRequiredMixin, ListView):
    model = BirthRegistration
    paginate_by = PAGINATE_BY

    def get_search_query(self):
        return self.request.GET.get('search') or self.request.GET.get('q')

    def get_queryset(self):
        qs = super().get_queryset().select_related('mother','doctor').order_by('-date_of_birth')
        q = self.get_search_query()
        gender = self.request.GET.get('gender')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if q:
            qs = qs.filter(Q(baby_name__icontains=q) | Q(mother__full_name__icontains=q) | Q(father_name__icontains=q))
        if start_date and end_date:
            qs = qs.filter(date_of_birth__range=[start_date, end_date])
        if gender:
            qs = qs.filter(gender=gender)
        return qs

class BirthListView(BirthFilterableListView):
    template_name = 'birth/birth_list.html'
    context_object_name = 'births'

class BirthCreateView(LoginRequiredMixin, CreateView):
    model = BirthRegistration
    form_class = BirthRegistrationForm
    template_name = 'birth/birth_form.html'
    success_url = reverse_lazy('birth_list')

    def form_valid(self, form):
        messages.success(self.request, "Birth record added successfully.")
        return super().form_valid(form)

class BirthDetailView(LoginRequiredMixin, DetailView):
    model = BirthRegistration
    template_name = 'birth/birth_detail.html'
    context_object_name = 'birth'

class BirthUpdateView(LoginRequiredMixin, UpdateView):
    model = BirthRegistration
    form_class = BirthRegistrationForm
    template_name = 'birth/birth_form.html'
    success_url = reverse_lazy('birth_list')

    def form_valid(self, form):
        messages.success(self.request, "Birth record updated.")
        return super().form_valid(form)

class BirthDeleteView(LoginRequiredMixin, DeleteView):
    model = BirthRegistration
    template_name = 'birth/birth_confirm_delete.html'
    success_url = reverse_lazy('birth_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Birth record deleted.")
        return super().delete(request, *args, **kwargs)




# -------------------------
# Blood Group CRUD
# -------------------------

class BloodBankDashboardView(TemplateView):
    template_name = "blood/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Total donors
        context["total_donors"] = Donor.objects.count()

        # Total blood donations made
        context["total_donations"] = BloodDonation.objects.count()

        # Total units in stock
        context["total_units"] = BloodStock.objects.aggregate(
            total=Sum("quantity")
        )["total"] or 0

        # Blood request counts
        context["pending_requests"] = BloodRequest.objects.filter(status="Pending").count()
        context["approved_requests"] = BloodRequest.objects.filter(status="Approved").count()
        context["issued_requests"] = BloodRequest.objects.filter(status="Issued").count()

        # Low stock alert (less than 5 units)
        context["low_stock"] = BloodStock.objects.filter(quantity__lt=5)

        # Recent donations (last 10)
        context["recent_donations"] = BloodDonation.objects.order_by("-donation_date")[:10]

        # Recent Blood Requests
        context["recent_requests"] = BloodRequest.objects.order_by("-request_date")[:10]

        return context

class BloodGroupListView(ListView):
    model = BloodGroup
    template_name = "blood/blood_group_list.html"
    context_object_name = "groups"


class BloodGroupCreateView(CreateView):
    model = BloodGroup
    form_class = BloodGroupForm
    template_name = "blood/blood_group_form.html"
    success_url = reverse_lazy("blood_group_list")


class BloodGroupUpdateView(UpdateView):
    model = BloodGroup
    form_class = BloodGroupForm
    template_name = "blood/blood_group_form.html"
    success_url = reverse_lazy("blood_group_list")


class BloodGroupDeleteView(DeleteView):
    model = BloodGroup
    template_name = "blood/blood_group_delete.html"
    success_url = reverse_lazy("blood_group_list")


# -------------------------
# Blood Stock
# -------------------------
class BloodStockListView(ListView):
    model = BloodStock
    template_name = "blood/blood_stock_list.html"
    context_object_name = "stocks"


# -------------------------
# Donor CRUD
# -------------------------

class DonorListView(ListView):
    model = Donor
    template_name = "blood/donor_list.html"
    context_object_name = "donors"


class DonorCreateView(CreateView):
    model = Donor
    form_class = DonorForm
    template_name = "blood/donor_form.html"
    success_url = reverse_lazy("donor_list")


class DonorUpdateView(UpdateView):
    model = Donor
    form_class = DonorForm
    template_name = "blood/donor_form.html"
    success_url = reverse_lazy("donor_list")


class DonorDeleteView(DeleteView):
    model = Donor
    template_name = "blood/donor_delete.html"
    success_url = reverse_lazy("donor_list")


class DonorDetailView(DetailView):
    model = Donor
    template_name = "blood/donor_detail.html"


# -------------------------
# Donations
# -------------------------

class DonationListView(ListView):
    model = BloodDonation
    template_name = "blood/donation_list.html"
    context_object_name = "donations"


class DonationCreateView(CreateView):
    model = BloodDonation
    form_class = BloodDonationForm
    template_name = "blood/donation_form.html"
    success_url = reverse_lazy("donation_list")


# -------------------------
# Department
# -------------------------
class DepartmentListView(ListView):
    model = Department
    template_name = "department/department_list.html"
    context_object_name = "departments"


class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "department/department_form.html"
    success_url = reverse_lazy("department_list")


class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = "department/department_form.html"
    success_url = reverse_lazy("department_list")


class DepartmentDetailView(DetailView):
    model = Department
    template_name = "department/department_detail.html"
    context_object_name = "dept"


class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = "department/department_confirm_delete.html"
    success_url = reverse_lazy("department_list")


# -------------------------
# Blood Requests
# -------------------------

class BloodRequestListView(ListView):
    model = BloodRequest
    template_name = "blood/blood_request_list.html"
    context_object_name = "requests"


class BloodRequestCreateView(CreateView):
    model = BloodRequest
    form_class = BloodRequestForm
    template_name = "blood/blood_request_form.html"
    success_url = reverse_lazy("blood_request_list")


class BloodRequestUpdateView(UpdateView):
    model = BloodRequest
    form_class = BloodRequestForm
    template_name = "blood/blood_request_form.html"
    success_url = reverse_lazy("blood_request_list")


class BloodRequestDeleteView(DeleteView):
    model = BloodRequest
    template_name = "blood/blood_request_delete.html"
    success_url = reverse_lazy("blood_request_list")


# -------------------------
# Issue Blood
# -------------------------

def issue_blood_view(request, pk):
    req = BloodRequest.objects.get(pk=pk)
    success = req.issue_blood()

    if success:
        messages.success(request, "Blood successfully issued!")
    else:
        messages.error(request, "Not enough stock to issue blood.")

    return redirect("blood_request_list")


# <======================================Doctor========================================>
@group_required('Doctor')
def doctor_dashboard(request):
    # Ensure only doctor can view
    doctor = get_object_or_404(Doctor, user=request.user)

    # Stats
    total_patients = Prescription.objects.filter(doctor=doctor).values('patient').distinct().count()
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    completed_appointments = Appointment.objects.filter(doctor=doctor, status='completed').count()
    scheduled_appointments = Appointment.objects.filter(doctor=doctor, status='scheduled').count()
    cancelled_appointments = Appointment.objects.filter(doctor=doctor, status='cancelled').count()
    total_prescriptions = Prescription.objects.filter(doctor=doctor).count()
    total_lab_exams = LabExamination.objects.filter(doctor=doctor).count()
    births=BirthRegistration.objects.all()
    bloods=BloodStock.objects.all()
    # Earnings (based on invoices tagged to this doctor)
    earnings = Invoice.objects.filter(
        service_type='consultation',
        patient__in=Prescription.objects.filter(doctor=doctor).values('patient'),
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Recent activity
    recent_appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')[:5]
    recent_prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-date')[:5]
    recent_lab_exams = LabExamination.objects.filter(doctor=doctor).order_by('-date')[:5]

    context = {
        'bloods':bloods,
        'births':births,
        'doctor': doctor,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'scheduled_appointments': scheduled_appointments,
        'cancelled_appointments': cancelled_appointments,
        'total_prescriptions': total_prescriptions,
        'total_lab_exams': total_lab_exams,
        'earnings': earnings,
        'recent_appointments': recent_appointments,
        'recent_prescriptions': recent_prescriptions,
        'recent_lab_exams': recent_lab_exams,
    }

    return render(request, 'dashboards/doctor.html', context)


@login_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    paginator = Paginator(doctors.order_by('-full_name'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'doctor/doctor_list.html', {'page_obj': page_obj})

@login_required
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


@group_required('Admin')
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, 'Record Inserted Successfully!')
            return redirect('doctor_list')
        else:
            print(form.errors)  # 🔥 مهم debug
    else:
        form = DoctorForm()
    return render(request, 'doctor/doctor_form.html', {'form': form})



@group_required('Admin')
def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)

    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor updated successfully.")
            return redirect('doctor_list')
    else:
        form = DoctorForm(instance=doctor)

    return render(request, 'doctor/doctor_form.html', {'form': form, 'doctor': doctor})


@group_required('Admin')
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, "Doctor deleted.")
        return redirect('doctor_list')
    return render(request, 'doctor/doctor_confirm_delete.html', {'doctor': doctor})


# <======================================Employee========================================>
@login_required
def employee_detail_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    return render(request, 'employee/employee_detail.html', {'employee':employee})

@login_required
def employee_list(request):
    employees = Employee.objects.all().order_by('-join_date','-id')
    departments = Department.objects.all()
    search = request.GET.get('search')
    gender = request.GET.get('gender')
    department = request.GET.get('department')
    join_date = request.GET.get('join_date')
    role = request.GET.get('role')

    if search:
        employees = employees.filter(full_name__icontains=search)
    if gender:
        employees = employees.filter(gender=gender)
    if department:
        employees = employees.filter(department=department)
    if join_date:
        employees = employees.filter(join_date=join_date)
    if role:
        employees = employees.filter(role=role)

    paginator = Paginator(employees.order_by('-join_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'employee/employee_list.html', {
        'page_obj': page_obj,'departments': departments,
    })

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES )
        if form.is_valid():
            employee = form.save(commit=False)
            employee.save()
            messages.success(request, 'Record Inserted Successfully !')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employee/employee_form.html', {'form': form})

@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, instance=employee)
    if form.is_valid():
        form.save()
        messages.success(request, "Employee updated successfully.")
        return redirect('employee_list')
    return render(request, 'employee/employee_form.html', {'form': form})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, "Employee deleted.")
        return redirect('employee_list')
    return render(request, 'employee/employee_confirm_delete.html', {'employee': employee})


# <======================================Patient========================================>
@login_required
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

@login_required
def patient_list(request):
    patients = Patient.objects.all().order_by('-registration_date','-id')
    departments = Department.objects.all()
    search = request.GET.get('search')
    gender = request.GET.get('gender')
    department = request.GET.get('department')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if search:
        patients = patients.filter(full_name__icontains=search)
    if gender:
        patients = patients.filter(gender=gender)
    if department:
        patients = patients.filter(department=department)
    if start_date and end_date:
        patients = patients.filter(registration_date__range=[start_date, end_date])

    paginator = Paginator(patients.order_by('-registration_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'patient/patient_list.html', {
        'page_obj': page_obj,'departments': departments,
    })

@login_required
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

@login_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if form.is_valid():
        form.save()
        messages.success(request, "Patient updated successfully.")
        return redirect('patient_list')
    return render(request, 'patient/patient_form.html', {'form': form})

@login_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, "Patient deleted.")
        return redirect('patient_list')
    return render(request, 'patient/patient_confirm_delete.html', {'patient': patient})



# <======================================Medicine========================================>
@login_required
def medicine_list(request):
    medicines = Medicine.objects.all()

    name = request.GET.get('name')
    generic_name = request.GET.get('generic_name')
    supplier = request.GET.get('supplier')

    if name:
        medicines = medicines.filter(name__icontains=name)
    if generic_name:
        medicines = medicines.filter(generic_name__icontains=generic_name)
    if supplier:
        medicines = medicines.filter(supplier__name__icontains=supplier)        
    
    paginator = Paginator(medicines.order_by('-expiry_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'medicine/medicine_list.html', {
        'page_obj': page_obj,
    })

@login_required
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

@login_required
def restock_medicine(request, pk):
    medicine = Medicine.objects.get(pk=pk)
    if request.method == "POST":
        qty = int(request.POST.get("quantity", 0))
        medicine.quantity += qty
        medicine.save()
        messages.success(request, f"{medicine.name} restocked by {qty}.")
        return redirect("medicine_detail", pk=medicine.id)
    return render(request, "pharmacy/restock_form.html", {"medicine": medicine})


@login_required
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

@login_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, instance=medicine)
    if form.is_valid():
        form.save()
        messages.success(request, "Medicine updated successfully.")
        return redirect('medicine_list')
    return render(request, 'medicine/medicine_form.html', {'form': form})


@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, "Medicine deleted.")
        return redirect('medicine_list')
    return render(request, 'medicine/medicine_confirm_delete.html', {'medicine': medicine})

# <======================================Supplier========================================>
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    search = request.GET.get('search')

    if search:
        suppliers = suppliers.filter(name__icontains=search)

    paginator = Paginator(suppliers.order_by('name'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'supplier/supplier_list.html', {'page_obj': page_obj})

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'supplier/detail.html', {'supplier': supplier})


@login_required
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


@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=supplier)
    if form.is_valid():
        form.save()
        messages.success(request, "Supplier updated successfully.")
        return redirect('supplier_list')
    return render(request, 'supplier/supplier_form.html', {'form': form})


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, "Supplier deleted.")
        return redirect('supplier_list')
    return render(request, 'supplier/supplier_confirm_delete.html', {'supplier': supplier})

# <======================================LabEximination========================================>

@group_required('Lab Rant')
def lab_dashboard(request):
    # Totals
    total_exams = LabExamination.objects.count()
    bloods=BloodStock.objects.all()

    # Monthly Chart Data
    current_year = datetime.now().year
    monthly_data = (
        LabExamination.objects.filter(date__year=current_year)
        .values_list('date__month')
        .annotate(count=Count('id'))
    )

    months = list(range(1, 13))
    exam_counts = [dict(monthly_data).get(m, 0) for m in months]

    # Recent Examinations
    recent_exams = LabExamination.objects.all().order_by('-id')[:10]

    context = {
        'bloods': bloods,
        'total_exams': total_exams,
        'months': months,
        'exam_counts': exam_counts,
        'recent_exams': recent_exams,
    }

    return render(request, 'dashboards/lab.html', context)

@login_required
def lab_list(request):
    lab_exams = LabExamination.objects.select_related("patient", "doctor").all().order_by("-date")
    patient = request.GET.get('patient')
    doctor = request.GET.get('doctor')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if patient:
        lab_exams = lab_exams.filter(patient__full_name__icontains=patient)
    if doctor:
        lab_exams = lab_exams.filter(doctor__full_name__icontains=doctor)       
    if start_date and end_date:
        lab_exams = lab_exams.filter(date__range=[start_date, end_date])

    paginator = Paginator(lab_exams.order_by('-date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "lab/lab_list.html", {"page_obj": page_obj})

# Detail of a single lab examination (with items)
@login_required
def lab_detail(request, pk):
    lab_exam = get_object_or_404(LabExamination, pk=pk)
    items = lab_exam.items.all()  # related_name="items" from LabExaminationItem
    return render(request, "lab/detail.html", {
        "lab_exam": lab_exam,
        "items": items
    })

@login_required
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
        units = request.POST.getlist("unit[]")
        normals = request.POST.getlist("normal[]")

        for exam_type, price, result ,unit, normal in zip(exam_types, prices, results, units, normals):
            if exam_type.strip():  # skip empty rows
                LabExaminationItem.objects.create(
                    lab_exam=lab_exam,
                    unit=unit,
                    normal=normal,
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



@login_required
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
        units = request.POST.getlist("unit[]")
        normals = request.POST.getlist("normal[]")
        results = request.POST.getlist("result[]")

        for exam_type, price, result, unit, normal in zip(exam_types, prices, results, units, normals):
            if exam_type.strip():  # Only save if type is provided
                LabExaminationItem.objects.create(
                    lab_exam=lab_exam,
                    unit=unit,
                    normal=normal,
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



@login_required
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
@login_required
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-appointment_date','-id')
    patient = request.GET.get('patient')
    doctor = request.GET.get('doctor')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if patient:
        appointments = appointments.filter(patient__full_name__icontains=patient)
    if doctor:
        appointments = appointments.filter(doctor__full_name__icontains=doctor)
    if status:
        appointments = appointments.filter(status=status)       
    if start_date and end_date:
        appointments = appointments.filter(appointment_date__range=[start_date, end_date])
    
    paginator = Paginator(appointments.order_by('-appointment_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'appointment/appointment_list.html', {'page_obj': page_obj})

@login_required
def appointment_create(request):
    form = AppointmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_form.html', {'form': form})

@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if form.is_valid():
        form.save()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_form.html', {'form': form})

@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_confirm_delete.html', {'appointment': appointment})


# <======================================Prescription========================================>
@login_required
def prescription_list(request):
    prescriptions = Prescription.objects.all().order_by("-date")
    patient = request.GET.get('patient')
    doctor = request.GET.get('doctor')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if patient:
        prescriptions = prescriptions.filter(patient__full_name__icontains=patient)
    if doctor:
        prescriptions = prescriptions.filter(doctor__full_name__icontains=doctor)       
    if start_date and end_date:
        prescriptions = prescriptions.filter(date__range=[start_date, end_date])

    paginator = Paginator(prescriptions.order_by('-date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'prescription/prescription_list.html', {
        'page_obj': page_obj,
    })

@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    return render(request, "prescription/prescription_detail.html", {
        "prescription": prescription
    })


@login_required
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



@login_required
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


@login_required
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

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all()

    search = request.GET.get('search')
    service_type = request.GET.get('service_type')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if search:
        invoices = invoices.filter(patient__full_name__icontains=search)
    if service_type:
        invoices = invoices.filter(service_type=service_type)
    if status:
        invoices = invoices.filter(status=status)        
    if start_date and end_date:
        invoices = invoices.filter(date__range=[start_date, end_date])

    total = invoices.aggregate(total=Sum('amount'))['total'] or 0

    paginator = Paginator(invoices.order_by('-date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'invoice/invoice_list.html', {
        'page_obj': page_obj,
        'total': total,
    })

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, "invoice/detail.html", {
        "invoice": invoice
    })

@login_required
def invoice_create(request):
    form = InvoiceForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('invoice_list')
    return render(request, 'invoice/invoice_form.html', {'form': form})

@login_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = InvoiceForm(request.POST or None, instance=invoice)
    if form.is_valid():
        form.save()
        return redirect('invoice_list')
    return render(request, 'invoice/invoice_form.html', {'form': form})

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('invoice_list')
    return render(request, 'invoice/invoice_confirm_delete.html', {'invoice': invoice})




# <======================================Expenses========================================>


# 📜 List with search & filter
@login_required
def expense_list(request):
    expenses = Expense.objects.all()

    search = request.GET.get('search')
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if search:
        expenses = expenses.filter(title__icontains=search)
    if category:
        expenses = expenses.filter(category=category)
    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])

    total = expenses.aggregate(total=Sum('amount'))['total'] or 0

    paginator = Paginator(expenses.order_by('-date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'expenses/expense_list.html', {
        'page_obj': page_obj,
        'total': total,
    })


@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    context = {
        'expense': expense,
    }
    return render(request, 'expenses/expense_detail.html', context)


# ➕ Create
@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.added_by = request.user
            expense.save()
            messages.success(request, "Expense added successfully ✅")
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add Expense'})

# ✏️ Edit
@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully ✅")
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Edit Expense'})

# ❌ Delete
@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


@login_required
def export_expenses_pdf(request):
    # 📄 PDF response setup
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # ✅ Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=20, alignment=1, textColor=colors.HexColor("#0d6efd"), spaceAfter=8)
    info_style = ParagraphStyle('info', fontSize=12, alignment=1, textColor=colors.grey, spaceAfter=4)
    table_header_style = ParagraphStyle('header', fontSize=11, textColor=colors.white, alignment=1)
    table_cell_style = styles["Normal"]

    # 🖼️ Logo at top (center)
    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo-dark.ico")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = "CENTER"
        elements.append(logo)
        elements.append(Spacer(1, 10))

    # 🏥 Hospital Info
    elements.append(Paragraph("Ghazni International Hospital", title_style))
    elements.append(Paragraph("Main Street, Ghazni City, Afghanistan", info_style))
    elements.append(Paragraph("Emergency: +93 700000000", info_style))
    elements.append(Spacer(1, 20))

    # 📊 Table Header
    data = [
        [
            Paragraph("<b>#</b>", table_header_style),
            Paragraph("<b>Title</b>", table_header_style),
            Paragraph("<b>Category</b>", table_header_style),
            Paragraph("<b>Amount (AFN)</b>", table_header_style),
            Paragraph("<b>Date</b>", table_header_style),
            Paragraph("<b>Added By</b>", table_header_style),
        ]
    ]

    # 🧾 Expense Rows
    expenses = Expense.objects.all().order_by("date")
    total_amount = 0
    for i, expense in enumerate(expenses, start=1):
        total_amount += expense.amount
        data.append([
            str(i),
            Paragraph(expense.title, table_cell_style),
            Paragraph(expense.category, table_cell_style),
            f"{expense.amount:.2f}",
            expense.date.strftime("%Y-%m-%d"),
            Paragraph(str(expense.added_by), table_cell_style),  # ✅ wrapped text
        ])

    # ➕ Total row
    data.append([
        "",
        "",
        Paragraph("<b>Total</b>", table_cell_style),
        Paragraph(f"<b>{total_amount:.2f}</b>", table_cell_style),
        "",
        "",
    ])

    # 🪄 Create table
    table = Table(data, colWidths=[30, 130, 100, 90, 90, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
    ]))

    elements.append(table)
    doc.build(elements)

    return response


@login_required
def export_expenses_excel(request):
    qs = get_filtered_expenses_from_request(request)
    total_amount = qs.aggregate(total=Sum('amount'))['total'] or 0

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Expenses"

    # Header rows — hospital name and contact
    ws.merge_cells('A1:F1')
    ws['A1'] = "Ghazni International Hospital"
    ws['A1'].font = Font(size=14, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')
    ws.merge_cells('A2:F2')
    ws['A2'] = "Main Street, Ghazni City, Afghanistan | Emergency: +93 700000000"
    ws['A2'].alignment = Alignment(horizontal='center')

    # Column headers
    headers = ['#', 'Title', 'Category', 'Amount (AFN)', 'Date', 'Added By']
    row_start = 4
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=row_start, column=col_num, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    # Data rows
    for idx, exp in enumerate(qs, start=1):
        r = row_start + idx
        ws.cell(row=r, column=1, value=idx)
        ws.cell(row=r, column=2, value=exp.title)
        ws.cell(row=r, column=3, value=exp.get_category_display())
        ws.cell(row=r, column=4, value=float(exp.amount))
        ws.cell(row=r, column=5, value=exp.date.strftime("%Y-%m-%d"))
        ws.cell(row=r, column=6, value=str(exp.added_by) if exp.added_by else "")

    # Total row
    total_row = row_start + qs.count() + 1
    ws.cell(row=total_row, column=3, value="Total")
    ws.cell(row=total_row, column=4, value=float(total_amount))
    ws.cell(row=total_row, column=4).font = Font(bold=True)

    # Auto column width
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                val = str(cell.value)
                if val:
                    max_length = max(max_length, len(val))
            except Exception:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[col_letter].width = adjusted_width

    # Prepare response
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# @group_required('Lab Rant')
# def lab_dashboard(request):
#     return render(request, 'dashboards/lab.html')

@group_required('Pharmacist')
def pharmacist_dashboard(request):
    total_medicines = Medicine.objects.count()
    low_stock = Medicine.objects.filter(quantity__lte=10).count()
    total_suppliers = Supplier.objects.count()
    total_prescriptions = PrescriptionItem.objects.count()
    total_sales = Invoice.objects.filter(service_type='medicine').aggregate(total=Sum('amount'))['total'] or 0
    

    # Recent Activities
    recent_prescriptions = PrescriptionItem.objects.select_related('prescription', 'medicine').order_by('-id')[:5]
    recent_sales = Invoice.objects.filter(service_type='medicine').order_by('-id')[:5]
    low_stock_medicines = Medicine.objects.filter(quantity__lte=10).order_by('quantity')[:5]

    context = {
        'total_medicines': total_medicines,
        'low_stock': low_stock,
        'total_suppliers': total_suppliers,
        'total_prescriptions': total_prescriptions,
        'total_sales': total_sales,
        'recent_prescriptions': recent_prescriptions,
        'recent_sales': recent_sales,
        'low_stock_medicines': low_stock_medicines,
    }
    return render(request, 'dashboards/pharmacist.html', context)


   

@group_required('Finance')
def finance_dashboard(request):
    # Total calculations
    total_income = Invoice.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense

    # Monthly chart data
    current_year = datetime.now().year
    income_data = (
        Invoice.objects.filter(date__year=current_year)
        .values_list('date__month')
        .annotate(total=Sum('amount'))
    )
    expense_data = (
        Expense.objects.filter(created_at__year=current_year)
        .values_list('created_at__month')
        .annotate(total=Sum('amount'))
    )

    months = list(range(1, 13))
    income_values = [dict(income_data).get(m, 0) for m in months]
    expense_values = [dict(expense_data).get(m, 0) for m in months]

    # Recent transactions
    recent_incomes = Invoice.objects.all().order_by('-id')[:5]
    recent_expenses = Expense.objects.all().order_by('-id')[:5]

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'months': months,
        'income_values': income_values,
        'expense_values': expense_values,
        'recent_incomes': recent_incomes,
        'recent_expenses': recent_expenses,
    }

    return render(request, 'dashboards/finance.html', context)






