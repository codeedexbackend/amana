# Generated by Django 5.0.1 on 2024-02-17 08:08

from django.db import migrations, models
from tailors.utils import generate_bill_number  # Import the bill generation function

class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0008_alter_order_order_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='AddCustomer',
            name='bill_number',
            field=models.CharField(max_length=50, unique=True, default=generate_bill_number),
        ),
    ]