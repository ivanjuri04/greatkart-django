# Generated by Django 5.0.1 on 2024-02-13 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='order_note',
            new_name='order_notes',
        ),
    ]
