# Generated by Django 4.1.4 on 2023-05-29 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0004_remove_productsell_client_remove_productsell_table_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsellcheck',
            name='order',
            field=models.CharField(blank=True, help_text='order ID-name', max_length=255, null=True),
        ),
    ]