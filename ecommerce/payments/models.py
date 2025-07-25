from django.db import models
from orders.models import Order
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference_id = models.CharField(max_length=100, verbose_name="شناسه پرداخت")
    is_successful = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
    
    def __str__(self):
        return f"Payment for Order #{self.order.order_number}"