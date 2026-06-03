
from django.db import models

from laundry.models import LaundryOrder   
class Bill(models.Model):
    order = models.OneToOneField(LaundryOrder, on_delete=models.CASCADE, null=True, blank=True)

    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    service = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.IntegerField()
    total = models.IntegerField()

    payment_status = models.CharField(max_length=20, default="Pending")
    date = models.DateTimeField(auto_now_add=True)


class PaymentTransaction(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    merchant_transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField()  # Store in paise for PhonePe or use Decimal
    status = models.CharField(max_length=20, default='PENDING') # PENDING, SUCCESS, FAILED
    provider_reference_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.merchant_transaction_id} - {self.status}"
