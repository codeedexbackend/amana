from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.utils.crypto import get_random_string


# Create your models here.

class TailorManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class AddTailors(AbstractUser):
    tailor = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, unique=True, null=True)
    password = models.CharField(max_length=10, null=True)
    mobile_number = models.CharField(max_length=15, unique=True, null=True)
    id = models.AutoField(primary_key=True)
    assigned_works = models.IntegerField(default=0)
    pending_works = models.IntegerField(default=0)
    upcoming_works = models.IntegerField(default=0)
    completed_works = models.IntegerField(default=0)

    objects = TailorManager()

    def __str__(self):
        return self.username


  # Convert to string before returning

class Customer(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    length = models.CharField(max_length=15)
    shoulder = models.CharField(max_length=15)

    SLEEVE_CHOICES = [
        ('half_sleeve', 'Half Sleeve'),
        ('full_sleeve', 'Full Sleeve'),
    ]
    sleeve_type = models.CharField(
        max_length=15,
        choices=SLEEVE_CHOICES,
        default='half_sleeve',
    )

    sleeve_length = models.CharField(max_length=15)
    neck = models.CharField(max_length=15)
    neck_round = models.CharField(max_length=15,null=True)
    collar = models.CharField(max_length=15,null=True)
    regal = models.CharField(max_length=15)
    loose = models.CharField(max_length=15)
    wrist = models.CharField(max_length=15,null=True)
    pocket = models.CharField(max_length=15)

    CUFF_CHOICES = [
        ('cuff', 'Cuff'),
        ('normal', 'Normal'),
    ]
    cuff_type = models.CharField(
        max_length=10,
        choices=CUFF_CHOICES,
        default='normal',
    )

    cuff_length = models.CharField(max_length=15)
    bottom1 = models.CharField(max_length=50)
    bottom2 = models.CharField(max_length=50)

    BUTTON_CHOICES = [
        ('bayyin_mahfi', 'Bayyin Mahfi'),
        ('zip_mahfi', 'Zip Mahfi'),
        ('mahfi', 'Mahfi'),
        ('button_bayyin', 'Button Bayyin'),
    ]
    button_type = models.CharField(
        max_length=15,
        choices=BUTTON_CHOICES,
    )

    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    tailor = models.ForeignKey(AddTailors, on_delete=models.SET_NULL, null=True)
       
    description = models.CharField(blank=True, null=True,max_length=100000)
    history = models.TextField(blank=True, null=True)
    bill_number = models.CharField(max_length=15, null=True, blank=True, unique=True)
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='assigned',
    )

    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Generate a unique bill number
            self.bill_number = get_unique_bill_number()
        super().save(*args, **kwargs)

def get_unique_bill_number():
    # Generate a unique bill number, you can customize the format as needed
    return f'Amana-{get_random_string(length=8)}'

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    details = models.TextField()
    order_date = models.DateField()
    delivery_date = models.DateField()

    def __str__(self):
        return f"Order for {self.customer.name} - {self.order_date}"
    
class Item(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100, null=True)
    item_quantity = models.PositiveIntegerField(null=True)
    item_price = models.FloatField(null=True)
    total_price = models.FloatField(null=True)

    def save(self, *args, **kwargs):
        # Calculate total price before saving
        self.total_price = self.item_quantity * self.item_price
        super().save(*args, **kwargs)