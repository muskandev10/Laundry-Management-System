from django.db import models
from django.contrib.auth.models import User

class LaundryOrder(models.Model):
    """Stores a laundry service request submitted by a customer."""

    LAUNDRY_TYPE_CHOICES = [
        ('Washing', 'Washing'),
        ('Ironing', 'Ironing'),
        ('Dry Cleaning', 'Dry Cleaning'),
        ('Wash & Iron', 'Wash & Iron'),
    ]

    CLOTH_CHOICES = [
        ('Top Wear', 'Top Wear'),
        ('Bottom Wear', 'Bottom Wear'),
        ('Bedsheets', 'Bedsheets'),
        ('Curtains', 'Curtains'),
        ('Heavy Clothes', 'Heavy Clothes'),
        ('Mixed Clothes', 'Mixed Clothes'),
    ]


    STATE_CHOICES = [
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True
    )
    full_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    state = models.CharField(max_length=100, choices=STATE_CHOICES)
    city = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    address = models.TextField()
    laundry_type = models.CharField(max_length=50, choices=LAUNDRY_TYPE_CHOICES)
    cloth_type = models.CharField(max_length=50, choices=CLOTH_CHOICES)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, default='')
    issued_date = models.DateField()
    delivery_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def price(self):
        """Calculate estimated price based on service type and weight."""
        price_list = {
            'washing': 40,
            'ironing': 30,
            'dry cleaning': 80,
            'wash & iron': 60,
        }
        service_text = self.laundry_type.lower()
        if 'wash & iron' in service_text:
            key = 'wash & iron'
        elif 'dry cleaning' in service_text:
            key = 'dry cleaning'
        elif 'ironing' in service_text:
            key = 'ironing'
        elif 'washing' in service_text:
            key = 'washing'
        else:
            key = None

        price_per_unit = price_list.get(key, 0)
        return int(price_per_unit * float(self.weight))

    def __str__(self):
        return f"Order #{self.pk} - {self.full_name}"


class OrderTracking(models.Model):
    """Tracks the status of a laundry order."""

    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Received'),
        (2, 'Out For Pickup'),
        (3, 'Washing'),
        (4, 'Ironing'),
        (5, 'Ready for Delivery'),
        (6, 'Out For Delivery'),
        (7, 'Delivered'),
        (8, 'Cancelled'),
    ]

    order = models.OneToOneField(
        LaundryOrder, on_delete=models.CASCADE, related_name='tracking'
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def get_status_display_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Unknown')

    def get_status_class(self):
        mapping = {
            0: 'status-pending',
            1: 'status-received',
            2: 'status-pickup',
            3: 'status-washing',
            4: 'status-ironing',
            5: 'status-ready',
            6: 'status-out-delivery',
            7: 'status-delivered',
            8: 'status-cancelled',
        }
        return mapping.get(self.status, 'status-pending')

    def __str__(self):
        return f"Tracking #{self.order.pk} - {self.get_status_display_label()}"
