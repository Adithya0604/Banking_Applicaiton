# Generated by Django 5.0.5 on 2025-03-21 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounttransaction',
            name='transactiontype',
            field=models.CharField(max_length=10),
        ),
    ]
