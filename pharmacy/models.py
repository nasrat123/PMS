# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# -------------------------------
# Patient model
# -------------------------------
class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]

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
# Doctor model
# -------------------------------
class Doctor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]

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

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

    def total_price(self):
        return self.medicine.selling_price * self.quantity

    def save(self, *args, **kwargs):
        """
        Adjust stock on create and update:
          - On create: reduce by quantity.
          - On update: compute delta; reduce or restock accordingly.
          - If medicine changed: restock old medicine qty, reduce new medicine qty.
        """
        if self.pk:
            old = PrescriptionItem.objects.get(pk=self.pk)

            if old.medicine_id != self.medicine_id:
                # Return old stock
                old.medicine.restock(old.quantity)
                # Take from new
                if self.medicine.quantity < self.quantity:
                    raise ValueError(f"Not enough stock for {self.medicine.name}")
                self.medicine.reduce_stock(self.quantity)
            else:
                delta = self.quantity - old.quantity
                if delta > 0:
                    if self.medicine.quantity < delta:
                        raise ValueError(f"Not enough stock for {self.medicine.name}")
                    self.medicine.reduce_stock(delta)
                elif delta < 0:
                    self.medicine.restock(-delta)
        else:
            # Create
            if self.medicine.quantity < self.quantity:
                raise ValueError(f"Not enough stock for {self.medicine.name}")
            self.medicine.reduce_stock(self.quantity)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Restock on delete
        self.medicine.restock(self.quantity)
        super().delete(*args, **kwargs)


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
