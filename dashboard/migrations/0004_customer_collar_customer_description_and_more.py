# Generated by Django 5.0.1 on 2024-02-21 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_rename_addtailor_addtailors'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='collar',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='description',
            field=models.CharField(blank=True, max_length=100000, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='neck_round',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='wrist',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='button_type',
            field=models.CharField(choices=[('bayyin_mahfi', 'Bayyin Mahfi'), ('zip_mahfi', 'Zip Mahfi'), ('mahfi', 'Mahfi'), ('button_bayyin', 'Button Bayyin')], max_length=15),
        ),
    ]