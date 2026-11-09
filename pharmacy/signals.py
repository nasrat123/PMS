
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MedicineRestock, StockTransaction


@receiver(post_save, sender=MedicineRestock)
def increase_stock_on_restock(sender, instance, created, **kwargs):

    # Only process newly created restock records
    if not created:
        return

    medicine = instance.medicine

    # Save the old and new stock quantities
    previous_quantity = medicine.quantity
    new_quantity = previous_quantity + instance.quantity_added

    medicine.quantity = new_quantity
    medicine.save(update_fields=["quantity"])

    # Record the stock transaction
    StockTransaction.objects.create(
        medicine=medicine,
        transaction_type="IN",
        quantity=instance.quantity_added,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        performed_by=instance.performed_by,
        note="Medicine restocked",
    )

