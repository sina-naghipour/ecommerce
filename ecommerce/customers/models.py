from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    phone = models.CharField(max_length=15, verbose_name="تلفن همراه")
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    newsletter = models.BooleanField(default=False, verbose_name="عضویت در خبرنامه")
    
    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"
    
    def __str__(self):
        return f"{self.user.get_full_name()}"


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, verbose_name="عنوان آدرس")
    receiver_name = models.CharField(max_length=100, verbose_name="نام تحویل گیرنده")
    phone = models.CharField(max_length=15, verbose_name="تلفن")
    province = models.CharField(max_length=50, verbose_name="استان")
    city = models.CharField(max_length=50, verbose_name="شهر")
    address = models.TextField(verbose_name="آدرس کامل")
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی")
    is_default = models.BooleanField(default=False, verbose_name="آدرس پیش‌فرض")
    
    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        ordering = ['-is_default']
    
    def __str__(self):
        return f"{self.title} - {self.city}"