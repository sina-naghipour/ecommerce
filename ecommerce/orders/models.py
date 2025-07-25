from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product
from customers.models import Customer, Address
from delivery.models import DeliveryMethod, Courier
import uuid
from faker import Faker

fake = Faker()
class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال آماده‌سازی'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'مرجوع شده'),
    )
    
    PAYMENT_METHODS = (
        ('online', 'پرداخت آنلاین'),
        ('cash', 'پرداخت در محل'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    order_number = models.CharField(
        max_length=20, 
        unique=True,
        editable=False,
        verbose_name="شماره سفارش"
    )
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.BooleanField(default=False, verbose_name="وضعیت پرداخت")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, verbose_name="آدرس ارسال")
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.PROTECT, verbose_name="روش ارسال")
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_code = models.CharField(max_length=50, blank=True, verbose_name="کد رهگیری")
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all()) + self.delivery_method.price
    
    @property
    def items_count(self):
        return self.items.count()
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        return fake.unique.bothify('ORD-####-???').upper()
    def get_status_choices(self):
        return self.ORDER_STATUS



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="قیمت واحد"
    )
    
    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.price


