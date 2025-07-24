from django.core.management.base import BaseCommand
from faker import Faker
from faker.providers import BaseProvider
import random
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

# Import your models
from products.models import Category, Product, ProductImage, ProductSpecification, InventoryLog
from customers.models import Customer, Address
from carts.models import Cart, CartItem
from delivery.models import DeliveryMethod, Courier
from orders.models import Order, OrderItem, Payment

User = get_user_model()
fake = Faker('fa_IR')  # Persian/Farsi locale

class PersianProductProvider(BaseProvider):
    def product_name(self):
        prefixes = ['لوازم', 'دستگاه', 'سیستم', 'کیت', 'ماشین', 'ابزار']
        categories = ['خانگی', 'صنعتی', 'اداری', 'دیجیتال', 'پزشکی', 'آرایشی']
        types = ['هوشمند', 'پیشرفته', 'حرفه‌ای', 'اقتصادی', 'فشرده', 'سبک']
        nouns = ['تمیزکننده', 'تهویه', 'نورپردازی', 'صوتی', 'تصویری', 'پخت‌وپز']
        
        return f"{self.random_element(prefixes)} {self.random_element(nouns)} {self.random_element(types)} {self.random_element(categories)}"

fake.add_provider(PersianProductProvider)

class Command(BaseCommand):
    help = 'Populates the database with fake data for all models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of records to create for each model'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(self.style.SUCCESS(f'Creating {count} records for each model...'))
        
        self.create_categories(count)
        self.create_products(count)
        self.create_users_and_customers(count)
        self.create_addresses(count)
        self.create_delivery_methods()
        self.create_couriers()
        self.create_carts_and_items(count)
        self.create_orders_and_payments(count)
        self.create_inventory_logs(count)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated the database!'))

    def create_categories(self, count):
        categories = []
        for i in range(count):
            parent = None
            if i > 2 and random.choice([True, False]):
                parent = Category.objects.order_by('?').first()
            
            category = Category.objects.create(
                name=fake.word() + " " + fake.word(),
                parent=parent,
                is_active=random.choice([True, False]))
                
            categories.append(category)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

    def create_products(self, count):
        categories = Category.objects.all()
        users = User.objects.all()
        
        for i in range(count):
            product = Product.objects.create(
                name=fake.product_name(),
                category=random.choice(categories),
                description=fake.paragraph(nb_sentences=5),
                base_price=random.randint(10000, 1000000),
                discount_price=random.choice([None, random.randint(5000, 900000)]),
                sku=fake.unique.bothify('SKU-####-???'),
                stock=random.randint(0, 100),
                threshold=random.randint(1, 10),
                is_active=random.choice([True, False]),
                is_featured=random.choice([True, False]),
                is_available=random.choice([True, False]),
                main_image='products/main/default.jpg',  # You need to have this image
                created_by=random.choice(users) if users else None
            )
            
            # Create product images
            for j in range(random.randint(1, 5)):
                ProductImage.objects.create(
                    product=product,
                    image='products/gallery/default.jpg',
                    alt_text=fake.sentence(),
                    is_featured=(j == 0)
                )
            
            # Create specifications
            specs = [
                ('وزن', f'{random.randint(100, 5000)} گرم'),
                ('ابعاد', f'{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)} سانتی‌متر'),
                ('رنگ', fake.color_name()),
                ('جنس', fake.word()),
                ('گارانتی', f'{random.randint(6, 36)} ماهه')
            ]
            
            for name, value in specs:
                ProductSpecification.objects.create(
                    product=product,
                    name=name,
                    value=value
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {count} products with images and specifications'))

    def create_users_and_customers(self, count):
        for i in range(count):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='testpass123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            
            Customer.objects.create(
                user=user,
                phone=fake.phone_number(),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=70),
                newsletter=random.choice([True, False])
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {count} users with customer profiles'))

    def create_addresses(self, count):
        customers = Customer.objects.all()
        for customer in customers:
            for i in range(random.randint(1, 3)):
                Address.objects.create(
                    customer=customer,
                    title=fake.word() + " " + fake.word(),
                    receiver_name=fake.name(),
                    phone=fake.phone_number(),
                    province=fake.state(),
                    city=fake.city(),
                    address=fake.address(),
                    postal_code=fake.postcode(),
                    is_default=(i == 0)
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created addresses for {customers.count()} customers'))

    def create_delivery_methods(self):
        methods = [
            ('پست پیشتاز', 'تحویل 2-3 روز کاری', 25000, 3),
            ('پست سفارشی', 'تحویل 4-7 روز کاری', 15000, 5),
            ('تیپاکس', 'تحویل 1-2 روز کاری', 35000, 2),
            ('پیک موتوری', 'تحویل همان روز', 20000, 1),
        ]
        
        for name, desc, price, days in methods:
            DeliveryMethod.objects.create(
                name=name,
                description=desc,
                price=price,
                estimated_days=days,
                is_active=True
            )
        
        self.stdout.write(self.style.SUCCESS('Created delivery methods'))

    def create_couriers(self):
        couriers = [
            ('اکبر محمدی', '09123456789'),
            ('رضا احمدی', '09129876543'),
            ('سارا حسینی', '09121112233'),
            ('علی کریمی', '09123334455'),
        ]
        
        for name, phone in couriers:
            Courier.objects.create(
                name=name,
                phone=phone,
                is_active=True
            )
        
        self.stdout.write(self.style.SUCCESS('Created couriers'))

    def create_carts_and_items(self, count):
        customers = Customer.objects.all()
        products = Product.objects.all()
        
        for customer in customers:
            cart, created = Cart.objects.get_or_create(customer=customer)
            
            # Add random items to cart
            for product in random.sample(list(products), random.randint(1, 5)):
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=random.randint(1, 5)
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created carts for {customers.count()} customers'))

    def create_orders_and_payments(self, count):
        customers = Customer.objects.all()
        delivery_methods = DeliveryMethod.objects.all()
        couriers = Courier.objects.all()
        statuses = [s[0] for s in Order.ORDER_STATUS]
        payment_methods = [p[0] for p in Order.PAYMENT_METHODS]
        
        for i in range(count):
            customer = random.choice(customers)
            address = random.choice(customer.addresses.all())
            delivery_method = random.choice(delivery_methods)
            
            order = Order.objects.create(
                customer=customer,
                order_number=fake.unique.bothify('ORD-####-???'),
                status=random.choice(statuses),
                payment_method=random.choice(payment_methods),
                payment_status=random.choice([True, False]),
                address=address,
                delivery_method=delivery_method,
                courier=random.choice(couriers) if random.choice([True, False]) else None,
                tracking_code=fake.bothify('TRK-######') if random.choice([True, False]) else '',
                notes=fake.sentence() if random.choice([True, False]) else ''
            )
            
            # Add order items
            cart = customer.cart
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.current_price
                )
            
            # Create payment if paid
            if order.payment_status:
                Payment.objects.create(
                    order=order,
                    amount=order.total_price,
                    reference_id=fake.unique.bothify('PAY-####-???'),
                    is_successful=True
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {count} orders with payments'))

    def create_inventory_logs(self, count):
        products = Product.objects.all()
        users = User.objects.all()
        
        for product in products:
            for i in range(random.randint(1, 5)):
                adjustment_type = random.choice(['set', 'add', 'subtract'])
                quantity = random.randint(1, 20)
                previous_stock = product.stock
                
                if adjustment_type == 'set':
                    new_stock = quantity
                elif adjustment_type == 'add':
                    new_stock = previous_stock + quantity
                else:
                    new_stock = max(0, previous_stock - quantity)
                
                InventoryLog.objects.create(
                    product=product,
                    user=random.choice(users),
                    adjustment_type=adjustment_type,
                    quantity=quantity,
                    previous_stock=previous_stock,
                    new_stock=new_stock,
                    notes=fake.sentence()
                )
                
                # Update product stock to the latest value
                product.stock = new_stock
                product.save()
        
        self.stdout.write(self.style.SUCCESS(f'Created inventory logs for {products.count()} products'))