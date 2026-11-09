from django.db import transaction

from pharmacy.models import (
    Medicine,
    Prescription,
    PrescriptionItem,
    StockTransaction,
)


def validate_prescription_items(items):

    medicine_ids = set()

    for item in items:

        medicine_id = item["medicine_id"]
        quantity = item["quantity"]

        # Quantity must be greater than zero
        if quantity <= 0:
            raise ValueError(
                "Medicine quantity must be greater than zero."
            )

        # Prevent duplicate medicine
        if medicine_id in medicine_ids:
            raise ValueError(
                "The same medicine cannot be added twice "
                "to the same prescription."
            )

        medicine_ids.add(medicine_id)


@transaction.atomic
def create_prescription(
    patient,
    doctor,
    diagnosis,
    regimen,
    items,
    user=None,
):
    # Validate prescription items first
    validate_prescription_items(items)

    # Do not create an empty prescription
    if not items:
        raise ValueError(
            "A prescription must contain at least one medicine."
        )

    # Create the prescription inside the transaction
    prescription = Prescription.objects.create(
        patient=patient,
        doctor=doctor,
        diagnosis=diagnosis,
        regimen=regimen,
    )

    for item in items:

        # Lock the medicine row while checking and updating stock
        medicine = Medicine.objects.select_for_update().filter(
            pk=item["medicine_id"],
            is_active=True,
        ).first()

        # Reject missing or inactive medicines
        if medicine is None:
            raise ValueError(
                "The selected medicine is inactive or does not exist."
            )

        quantity = item["quantity"]

        # Validate quantity
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
            raise ValueError(
                f"Invalid quantity for {medicine.name}."
            )

        # Check available stock
        if quantity > medicine.quantity:
            raise ValueError(
                f"Not enough stock for {medicine.name}. "
                f"Available: {medicine.quantity}, "
                f"Requested: {quantity}"
            )

        # Save old stock
        previous_quantity = medicine.quantity

        # Reduce stock
        medicine.quantity -= quantity

        medicine.save(
            update_fields=["quantity"]
        )

        # Create stock history
        StockTransaction.objects.create(
            medicine=medicine,
            transaction_type="OUT",
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=medicine.quantity,
            prescription=prescription,
            performed_by=user,
            note="Medicine issued through prescription",
        )

        # Create prescription item
        PrescriptionItem.objects.create(
            prescription=prescription,
            medicine=medicine,
            quantity=quantity,
            dosage=item.get("dosage", ""),
        )

    return prescription


@transaction.atomic
def update_prescription(
    prescription,
    patient,
    doctor,
    diagnosis,
    regimen,
    items,
    user=None,
):

    validate_prescription_items(items)

    old_items = list(
        PrescriptionItem.objects.select_for_update().filter(
            prescription=prescription
        )
    )

    # --------------------------------
    # Return old medicines to stock
    # --------------------------------

    for old_item in old_items:

        medicine = Medicine.objects.select_for_update().get(
            pk=old_item.medicine_id
        )

        previous_quantity = medicine.quantity

        medicine.quantity += old_item.quantity

        medicine.save(
            update_fields=["quantity"]
        )

        # Record returned stock
        StockTransaction.objects.create(
            medicine=medicine,
            transaction_type="RETURN",
            quantity=old_item.quantity,
            previous_quantity=previous_quantity,
            new_quantity=medicine.quantity,
            prescription=prescription,
            performed_by=user,
            note="Old medicine returned during prescription update",
        )

    # --------------------------------
    # Update prescription information
    # --------------------------------

    prescription.patient = patient
    prescription.doctor = doctor
    prescription.diagnosis = diagnosis
    prescription.regimen = regimen

    prescription.save()

    # --------------------------------
    # Delete old prescription items
    # --------------------------------

    PrescriptionItem.objects.filter(
        prescription=prescription
    ).delete()

    # --------------------------------
    # Add new prescription items
    # --------------------------------

    for item in items:

        medicine = Medicine.objects.select_for_update().get(
            pk=item["medicine_id"]
        )

        quantity = item["quantity"]

        if quantity > medicine.quantity:
            raise ValueError(
                f"Not enough stock for {medicine.name}. "
                f"Available: {medicine.quantity}, "
                f"Requested: {quantity}"
            )

        previous_quantity = medicine.quantity

        medicine.quantity -= quantity

        medicine.save(
            update_fields=["quantity"]
        )

        # Record new OUT transaction
        StockTransaction.objects.create(
            medicine=medicine,
            transaction_type="OUT",
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=medicine.quantity,
            prescription=prescription,
            performed_by=user,
            note="New medicine issued during prescription update",
        )

        PrescriptionItem.objects.create(
            prescription=prescription,
            medicine=medicine,
            quantity=quantity,
            dosage=item.get("dosage", ""),
        )

    return prescription


@transaction.atomic
def delete_prescription(
    prescription,
    user=None,
):

    items = list(
        PrescriptionItem.objects.select_for_update().filter(
            prescription=prescription
        )
    )

    # --------------------------------
    # Return medicines to stock
    # --------------------------------

    for item in items:

        medicine = Medicine.objects.select_for_update().get(
            pk=item.medicine_id
        )

        previous_quantity = medicine.quantity

        medicine.quantity += item.quantity

        medicine.save(
            update_fields=["quantity"]
        )

        # Record RETURN transaction
        StockTransaction.objects.create(
            medicine=medicine,
            transaction_type="RETURN",
            quantity=item.quantity,
            previous_quantity=previous_quantity,
            new_quantity=medicine.quantity,
            prescription=prescription,
            performed_by=user,
            note="Medicine returned after prescription deletion",
        )

    # Delete prescription
    prescription.delete()
