import uuid
from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User # <-- NEW: Import User model

class Wholesaler(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True) 
    image = CloudinaryField('image', blank=True, null=True) 
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name

class Product(models.Model):
    categories = models.ManyToManyField(Category, related_name='products')
    wholesaler = models.ForeignKey(Wholesaler, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Supplier: {self.wholesaler.name})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=50, help_text="e.g., Size, Color")
    value = models.CharField(max_length=50, help_text="e.g., XL, Red")
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Add or subtract from base price")
    stock = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"

class HeroBanner(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200, blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    link = models.CharField(max_length=255, default='#', help_text="Where should the button go? e.g., /category/sports")
    button_text = models.CharField(max_length=50, default="Shop Now")
    
    POSITION_CHOICES = [
        ('LEFT', 'Left Small Box'),
        ('CENTER', 'Center Large Box'),
        ('RIGHT', 'Right Small Box'),
    ]
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.position}: {self.title}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    # NEW: Link the order to a registered user
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"Order {self.id}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, related_name='order_items', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    wholesaler = models.ForeignKey(Wholesaler, related_name='order_items', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Item {self.id} in Order {self.order.id}"

    def get_cost(self):
        return self.price * self.quantity