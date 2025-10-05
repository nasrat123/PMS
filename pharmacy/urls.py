from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # Authentication URLs
    path('login/', views.login_view, name='login'),
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
    path('redirect-dashboard/', views.redirect_dashboard, name='redirect_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/reception/', views.reception_dashboard, name='reception_dashboard'),
    path('dashboard/lab/', views.lab_dashboard, name='lab_dashboard'),
    path('dashboard/pharmacist/', views.pharmacist_dashboard, name='pharmacist_dashboard'),
    path('dashboard/finance/', views.finance_dashboard, name='finance_dashboard'),

    path('doctors/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:pk>/edit/', views.doctor_update, name='doctor_update'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),


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

    # Lab Examination URLs
    path('lab/', views.lab_list, name='lab_list'),
    path('labd/', views.lab_dashboard, name='lab_dashboard'),
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



]