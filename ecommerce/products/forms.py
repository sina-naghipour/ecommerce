from django import forms
from .models import Product, Category, ProductImage, ProductSpecification
from django.core.exceptions import ValidationError
from .models import Product, Category
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 
            'base_price', 'discount_price',
            'stock', 'threshold', 'is_active',
            'is_featured', 'is_available', 'main_image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'main_image': forms.ClearableFileInput(attrs={
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        # Remove any SKU validation if it exists
        if 'sku' in self.errors:
            del self.errors['sku']
        return cleaned_data
    
    def clean_main_image(self):
        image = self.cleaned_data.get('main_image')
        if not image:
            return None
        # Size validation
        if image.size > 4*1024*1024:
            raise ValidationError("حجم تصویر نباید بیشتر از 4 مگابایت باشد")
        
        try:
            # Create a copy of the image file in memory
            img_data = image.read()
            img = Image.open(io.BytesIO(img_data))
            
            # Validate dimensions
            if img.width > 2000 or img.height > 2000:
                raise ValidationError("ابعاد تصویر نباید بیشتر از 2000x2000 پیکسل باشد")
            
            # Create a new file object that won't get closed
            img_io = io.BytesIO()
            img.save(img_io, format=img.format)
            new_image = InMemoryUploadedFile(
                img_io,
                'ImageField',
                image.name,
                image.content_type,
                len(img_io.getvalue()),
                None
            )
            new_image.seek(0)
            return new_image
            
        except Exception as e:
            raise ValidationError("تصویر معتبر نیست")
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_featured']

class ProductSpecificationForm(forms.ModelForm):
    class Meta:
        model = ProductSpecification
        fields = ['name', 'value']

class InventoryAdjustmentForm(forms.Form):
    ADJUSTMENT_CHOICES = (
        ('set', 'تنظیم مقدار دقیق'),
        ('add', 'افزایش موجودی'),
        ('subtract', 'کاهش موجودی'),
    )
    
    adjustment_type = forms.ChoiceField(choices=ADJUSTMENT_CHOICES)
    quantity = forms.IntegerField(min_value=0)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))

class ProductFilterForm(forms.Form):
    q = forms.CharField(required=False, label='جستجو')
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), 
        required=False, 
        label='دسته بندی'
    )
    status = forms.ChoiceField(
        choices=[('', 'همه'), ('active', 'فعال'), ('draft', 'پیش نویس')],
        required=False,
        label='وضعیت'
    )