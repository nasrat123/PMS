# models.py

from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# -------------------------------
# Department model
# -------------------------------
class Department(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=15)
    about = models.TextField()

    def __str__(self):
        return self.name
 

# -------------------------------
# Patient model
# -------------------------------
class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact = models.CharField(max_length=15)
    address = models.TextField()
    sick_type = models.TextField()
    registration_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.full_name


# -------------------------------
# Employee model
# -------------------------------
class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    photo = models.ImageField(
        upload_to='employes/',
        blank=True,
        null=True
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    employee_id = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact = models.CharField(max_length=15)
    role = models.CharField(max_length=15)
    address = models.TextField()
    join_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name



# -------------------------------
# Doctor model
# -------------------------------
class Doctor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    photo = models.ImageField(
        upload_to='doctors/',
        blank=True,
        null=True
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    available_days = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    education = models.TextField()
    experience = models.TextField()

    def __str__(self):
        return self.full_name   # ✅ safer than user.get_full_name()


# -------------------------------
# Blood model
# -------------------------------
class BloodGroup(models.Model):
    BLOOD_TYPES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("O+", "O+"), ("O-", "O-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
    ]

    name = models.CharField(max_length=5, choices=BLOOD_TYPES, unique=True)

    def __str__(self):
        return self.name


class BloodStock(models.Model):
    blood_group = models.OneToOneField(BloodGroup, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)  # in units/bags

    def __str__(self):
        return f"{self.blood_group} - {self.quantity} Units"


class Donor(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    full_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.ForeignKey(BloodGroup, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    last_donation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.blood_group})"


class BloodDonation(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    blood_group = models.ForeignKey(BloodGroup, on_delete=models.CASCADE)
    units = models.PositiveIntegerField(default=1)
    donation_date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Update stock automatically when donation saved"""
        super().save(*args, **kwargs)
        stock, created = BloodStock.objects.get_or_create(blood_group=self.blood_group)
        stock.quantity += self.units
        stock.save()

    def __str__(self):
        return f"Donation: {self.donor} - {self.units} Units"


class BloodRequest(models.Model):
    STATUS = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Issued", "Issued"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    blood_group = models.ForeignKey(BloodGroup, on_delete=models.CASCADE)
    units_required = models.PositiveIntegerField(default=1)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="Pending")
    request_date = models.DateTimeField(auto_now_add=True)
    issued_date = models.DateTimeField(null=True, blank=True)

    def issue_blood(self):
        """Decrease blood stock when issued"""
        stock = BloodStock.objects.get(blood_group=self.blood_group)
        if stock.quantity >= self.units_required:
            stock.quantity -= self.units_required
            stock.save()
            self.status = "Issued"
            self.issued_date = timezone.now()
            self.save()
            return True
        return False

    def __str__(self):
        return f"Request {self.patient} - {self.blood_group}"


# -------------------------------
# Birht Regisration model
# -------------------------------
class BirthRegistration(models.Model):
    GENDER = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]

    DELIVERY_TYPE = [
        ("Normal", "Normal Delivery"),
        ("Cesarean", "Cesarean (C-Section)"),
        ("Assisted", "Assisted Delivery"),
    ]

    baby_name = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER)
    weight_kg = models.DecimalField(max_digits=4, decimal_places=2, help_text="Baby weight in Kg")

    date_of_birth = models.DateField(default=timezone.now)
    time_of_birth = models.TimeField(default=timezone.now)

    mother = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="mother_births")
    father_name = models.CharField(max_length=150, null=True, blank=True)
    address = models.CharField(max_length=255)

    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPE)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Birth Record - {self.baby_name or 'Baby'} ({self.date_of_birth})"


# -------------------------------
# Supplier model
# -------------------------------
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    about = models.TextField()

    def __str__(self):
        return self.name


# -------------------------------
# Medicine model
# -------------------------------
class Medicine(models.Model):
    name = models.CharField(max_length=100)
    generic_name = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    batch_no = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    def __str__(self):
        return f"{self.name} ({self.batch_no})"

    def restock(self, amount):
        """Increase medicine quantity by given amount"""
        self.quantity += amount
        self.save()

    def reduce_stock(self, amount):
        """Decrease medicine quantity (if enough stock)"""
        if amount > self.quantity:
            raise ValueError(f"Not enough stock for {self.name}")
        self.quantity -= amount
        self.save()


# -------------------------------
# Medicine Restock model
# -------------------------------
class MedicineRestock(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity_added = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="medicine_restocks")

    def __str__(self):
        return f"{self.medicine.name} restocked by {self.quantity_added}"



# -------------------------------
# Lab Examination (Parent Model)
# -------------------------------
class LabExamination(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"LabExamination for {self.patient.full_name} on {self.date}"

    def total_cost(self):
        return sum(item.price for item in self.items.all())



# -------------------------------
# LabExaminationItem (Child Model)
# -------------------------------
class LabExaminationItem(models.Model):
    lab_exam = models.ForeignKey(
        LabExamination,
        on_delete=models.CASCADE,
        related_name="items"
    )
    examination_type = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    normal = models.CharField(max_length=100)
    result = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.examination_type} - {self.lab_exam.patient.full_name}"


# -------------------------------
# Appointment model
# -------------------------------
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ]
    )

    def __str__(self):
        return f"{self.patient.full_name} with {self.doctor.full_name}"


# -------------------------------
# Prescription model
# -------------------------------
class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    medicines = models.ManyToManyField("Medicine", through="PrescriptionItem")
    diagnosis = models.TextField()
    regimen = models.TextField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Prescription for {self.patient.full_name}"

    def total_cost(self):
        return sum(item.total_price() for item in self.items.all())


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="items"
    )
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    dosage = models.CharField(max_length=100)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["prescription","medicine"],
                name="unique_medicine_per_prescription"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="prescription_item_quantity_gt_zero"
            ),

        ]
    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

    def total_price(self):
        return self.medicine.selling_price * self.quantity



# -------------------------------
# Invoice model (for Finance role)
# -------------------------------
class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_type = models.CharField(
        max_length=50,
        choices=[
            ('consultation', 'Consultation'),
            ('lab', 'Lab Test'),
            ('medicine', 'Medicine'),
            ('other', 'Other'),
        ]
    )
    narrative = models.TextField()  
    status = models.CharField(
        max_length=10,
        choices=[
            ('paid', 'Paid'),
            ('unpaid', 'Unpaid')
        ]
    )

    def __str__(self):
        return f"Invoice for {self.patient.full_name} - {self.service_type}"


# -------------------------------
# StockTransaction Model
# -------------------------------
class StockTransaction(models.Model):

    TRANSACTION_TYPES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
        ("RETURN", "Stock Return"),
        ("ADJUSTMENT", "Adjustment"),
    ]

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="stock_transactions"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    quantity = models.PositiveIntegerField()

    previous_quantity = models.PositiveIntegerField()

    new_quantity = models.PositiveIntegerField()

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_transactions"
    )

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_transactions"
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.medicine.name} - "
            f"{self.transaction_type} - "
            f"{self.quantity}"
        )


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('salary', 'Salary'),
        ('utilities', 'Utilities'),
        ('supplies', 'Supplies'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.amount}"
