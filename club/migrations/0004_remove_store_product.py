# Generated by Django 4.1.4 on 2023-05-22 07:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0003_alter_store_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='product',
        ),
    ]