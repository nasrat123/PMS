from django.urls import path, include
from . import views
from .views import (
    DepartmentListView,
    DepartmentCreateView,
    DepartmentUpdateView,
    DepartmentDetailView,
    DepartmentDeleteView,
)

from django.contrib.auth import views as auth_views

urlpatterns = [

    # Authentication URLs
    path('', views.login_view, name='login'),
    # path('profile/', views.userprofile, name='userprofile'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Password reset URLs (optional)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),
         
    path('search/', views.search_all, name='search_all'),
    path('profile/', views.profile_view, name='profile_view'),
    path('redirect-dashboard/', views.redirect_dashboard, name='redirect_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/reception/', views.reception_dashboard, name='reception_dashboard'),
    path('dashboard/lab/', views.lab_dashboard, name='lab_dashboard'),
    path('dashboard/pharmacist/', views.pharmacist_dashboard, name='pharmacist_dashboard'),
    path('dashboard/finance/', views.finance_dashboard, name='finance_dashboard'),
    path("dashboard/", views.BloodBankDashboardView.as_view(), name="blood_dashboard"),

   
    # Blood Groups
    path("groups/", views.BloodGroupListView.as_view(), name="blood_group_list"),
    path("groups/add/", views.BloodGroupCreateView.as_view(), name="blood_group_add"),
    path("groups/<int:pk>/edit/", views.BloodGroupUpdateView.as_view(), name="blood_group_edit"),
    path("groups/<int:pk>/delete/", views.BloodGroupDeleteView.as_view(), name="blood_group_delete"),

    # Blood Stock
    path("stock/", views.BloodStockListView.as_view(), name="blood_stock_list"),

    # Donor CRUD
    path("donors/", views.DonorListView.as_view(), name="donor_list"),
    path("donors/add/", views.DonorCreateView.as_view(), name="donor_add"),
    path("donors/<int:pk>/edit/", views.DonorUpdateView.as_view(), name="donor_edit"),
    path("donors/<int:pk>/delete/", views.DonorDeleteView.as_view(), name="donor_delete"),
    path("donors/<int:pk>/detail/", views.DonorDetailView.as_view(), name="donor_detail"),

    # Blood Donations
    path("donations/", views.DonationListView.as_view(), name="donation_list"),
    path("donations/add/", views.DonationCreateView.as_view(), name="donation_add"),

    # Blood Requests
    path("requests/", views.BloodRequestListView.as_view(), name="blood_request_list"),
    path("requests/add/", views.BloodRequestCreateView.as_view(), name="blood_request_add"),
    path("requests/<int:pk>/edit/", views.BloodRequestUpdateView.as_view(), name="blood_request_edit"),
    path("requests/<int:pk>/delete/", views.BloodRequestDeleteView.as_view(), name="blood_request_delete"),
    path("requests/<int:pk>/issue/", views.issue_blood_view, name="issue_blood"),

    path('birth/', views.BirthListView.as_view(), name='birth_list'),
    path('birth/add/', views.BirthCreateView.as_view(), name='birth_add'),
    path('birth/<int:pk>/', views.BirthDetailView.as_view(), name='birth_detail'),
    path('birth/<int:pk>/edit/', views.BirthUpdateView.as_view(), name='birth_edit'),
    path('birth/<int:pk>/delete/', views.BirthDeleteView.as_view(), name='birth_delete'),


    path('doctors/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:pk>/edit/', views.doctor_update, name='doctor_update'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),


    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail_view, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail_view, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),

    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/add/', views.medicine_create, name='medicine_create'),
    path('medicines/<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('medicines/<int:pk>/edit/', views.medicine_update, name='medicine_update'),
    path('medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),


    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    path('departments/', DepartmentListView.as_view(), name="department_list"),
    path("departments/add/", DepartmentCreateView.as_view(), name="department_add"),
    path("departments/<int:pk>/edit/", DepartmentUpdateView.as_view(), name="department_edit"),
    path("departments/<int:pk>/", DepartmentDetailView.as_view(), name="department_detail"),
    path("departments/<int:pk>/delete/", DepartmentDeleteView.as_view(), name="department_delete"),

    # Lab Examination URLs
    path('lab/', views.lab_list, name='lab_list'),
    path('lab/<int:pk>/', views.lab_detail, name='lab_detail'),
    path('lab/create/', views.lab_create, name='lab_create'),
    path('lab/edit/<int:pk>/', views.lab_update, name='lab_update'),
    path('lab/delete/<int:pk>/', views.lab_delete, name='lab_delete'),

    # Appointment URLs
    path('appointment/', views.appointment_list, name='appointment_list'),
    path('appointment/create/', views.appointment_create, name='appointment_create'),
    path('appointment/update/<int:pk>/', views.appointment_update, name='appointment_update'),
    path('appointment/delete/<int:pk>/', views.appointment_delete, name='appointment_delete'),

    # Prescription URLs
    path('prescription/', views.prescription_list, name='prescription_list'),
    path('prescription/create/', views.prescription_create, name='prescription_create'),
    path("prescription/<int:pk>/", views.prescription_detail, name="prescription_detail"),
    path("prescription/<int:pk>/edit/", views.prescription_edit, name="prescription_edit"),
    path("prescription/<int:pk>/delete/", views.prescription_delete, name="prescription_delete"),


    # Invoice URLs
    path('invoice/', views.invoice_list, name='invoice_list'),
    path('invoice/create/', views.invoice_create, name='invoice_create'),
    path("invoice/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path('invoice/update/<int:pk>/', views.invoice_update, name='invoice_update'),
    path('invoice/delete/<int:pk>/', views.invoice_delete, name='invoice_delete'),
   
    # Expense URLs
    path('expenses/', views.expense_list, name='expense_list'),
    path('expense/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/add/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # Exports
    path('expenses/export/pdf/', views.export_expenses_pdf, name='expense_export_pdf'),
    path('expenses/export/excel/', views.export_expenses_excel, name='expense_export_excel'),



]