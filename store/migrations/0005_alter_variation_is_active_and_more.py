# Generated by Django 4.2.5 on 2024-01-16 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_variation_variation_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='is_active',
            field=models.CharField(default=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('color', 'color'), ('size', 'size')], max_length=100),
        ),
        migrations.AlterField(
            model_name='variation',
            name='variation_value',
            field=models.CharField(max_length=100),
        ),
    ]
