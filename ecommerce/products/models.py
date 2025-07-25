from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import uuid

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='children', verbose_name="دسته‌بندی والد")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)



def get_product_upload_path(instance, filename):
    """Generate safe upload path in 'files' directory"""
    # Get file extension
    ext = filename.split('.')[-1].lower()
    
    # Generate safe filename (product name + random string)
    safe_name = f"{slugify(instance.name) or 'product'}-{uuid.uuid4().hex[:8]}.{ext}"
    
    # Return path with SKU folder under 'files' directory
    if instance.sku:
        return f'files/{instance.sku}/{safe_name}'
    return f'files/unknown/{safe_name}'

class Product(models.Model):
    # Basic Information
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, 
                               related_name='products', verbose_name="دسته‌بندی")
    description = models.TextField(verbose_name="توضیحات", blank=True)
    
    # Pricing
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="قیمت پایه"
    )
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="قیمت با تخفیف"
    )
    
    # Inventory
    sku = models.CharField(max_length=50, unique=True, verbose_name="کد محصول")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی")
    threshold = models.PositiveIntegerField(
        default=5, 
        verbose_name="حداقل موجودی برای هشدار"
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_featured = models.BooleanField(default=False, verbose_name="پیشنهاد ویژه")
    is_available = models.BooleanField(default=True, verbose_name="موجود")
    
    # Media
    main_image = ProcessedImageField(
        upload_to=get_product_upload_path,
        processors=[ResizeToFill(800, 800)],
        format='JPEG',
        options={'quality': 90},
        blank=True,
        null=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='products_created',
        verbose_name="ایجاد شده توسط"
    )
    
    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        
        if not self.sku:
            category_part = slugify(self.category.name[:3]).upper() if self.category else 'PROD'
            name_part = slugify(self.name[:3]).upper() if self.name else 'GEN'
            random_part = uuid.uuid4().hex[:6].upper()  # 6-character random string
            
            self.sku = f"{category_part}-{name_part}-{random_part}"
        
        if self.pk:
            try:
                old = Product.objects.get(pk=self.pk)
                if old.main_image and old.main_image != self.main_image:
                    old.main_image.delete(save=False)
            except Product.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    @property
    def current_price(self):
        """Returns the active price (discounted if available)"""
        return self.discount_price if self.discount_price else self.base_price
    
    @property
    def discount_percentage(self):
        """Calculates discount percentage if available"""
        if self.discount_price:
            return int(((self.base_price - self.discount_price) / self.base_price) * 100)
        return 0
    
    def is_in_stock(self):
        """Check if product is available and has stock"""
        return self.is_available and self.stock > 0
    
    def is_low_stock(self):
        """Check if stock is below threshold"""
        return self.stock <= self.threshold


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="محصول"
    )
    image = models.ImageField(upload_to='products/gallery/', verbose_name="تصویر")
    alt_text = models.CharField(max_length=100, blank=True, verbose_name="متن جایگزین")
    is_featured = models.BooleanField(default=False, verbose_name="تصویر شاخص")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصولات"
        ordering = ['-is_featured', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='specifications',
        verbose_name="محصول"
    )
    name = models.CharField(max_length=100, verbose_name="ویژگی")
    value = models.CharField(max_length=255, verbose_name="مقدار")
    
    class Meta:
        verbose_name = "مشخصه محصول"
        verbose_name_plural = "مشخصات محصول"
    
    def __str__(self):
        return f"{self.name}: {self.value}"


class InventoryLog(models.Model):
    ADJUSTMENT_TYPES = (
        ('set', 'تنظیم مقدار دقیق'),
        ('add', 'افزایش موجودی'),
        ('subtract', 'کاهش موجودی'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    adjustment_type = models.CharField(max_length=10, choices=ADJUSTMENT_TYPES)
    quantity = models.PositiveIntegerField()
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "تاریخچه موجودی"
        verbose_name_plural = "تاریخچه موجودی‌ها"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_adjustment_type_display()} - {self.product.name}"