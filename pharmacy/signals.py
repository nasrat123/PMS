from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PrescriptionItem, Medicine

# Decrease stock when prescription item is created
@receiver(post_save, sender=PrescriptionItem)
def decrease_stock_on_prescription(sender, instance, created, **kwargs):
    if created:  # only on new prescription item
        medicine = instance.medicine
        medicine.quantity -= instance.quantity
        medicine.save()

# Increase stock if prescription item is deleted (e.g., cancelled)
@receiver(post_delete, sender=PrescriptionItem)
def increase_stock_on_delete(sender, instance, **kwargs):
    medicine = instance.medicine
    medicine.quantity += instance.quantity
    medicine.save()


@receiver(post_save, sender=MedicineRestock)
def increase_stock_on_restock(sender, instance, created, **kwargs):
    if created:
        medicine = instance.medicine
        medicine.quantity += instance.quantity_added
        medicine.save()
