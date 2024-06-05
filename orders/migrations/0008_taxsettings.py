# Generated by Django 5.0.1 on 2024-06-04 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_alter_order_payment_alter_orderproduct_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tax_percentage', models.DecimalField(decimal_places=2, default=25.0, max_digits=5)),
            ],
        ),
    ]
