# Generated by Django 5.0.1 on 2024-02-19 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0030_rename_tailorname_addtailor_tailor_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='addtailor',
            old_name='tailor_name',
            new_name='tailor',
        ),
    ]
