from django.db import models
from django.core.validators import MinValueValidator

class DeliveryMethod(models.Model):
    name = models.CharField(max_length=50, verbose_name="نام روش ارسال")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="هزینه ارسال"
    )
    estimated_days = models.PositiveSmallIntegerField(verbose_name="زمان تحویل تخمینی (روز)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "روش ارسال"
        verbose_name_plural = "روش‌های ارسال"
    
    def __str__(self):
        return self.name


class Courier(models.Model):
    name = models.CharField(max_length=50, verbose_name="نام پیک")
    phone = models.CharField(max_length=15, verbose_name="تلفن")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "پیک"
        verbose_name_plural = "پیک‌ها"
    
    def __str__(self):
        return self.name