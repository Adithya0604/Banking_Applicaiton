# Generated by Django 5.0.6 on 2024-06-03 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounttransaction',
            name='Status',
            field=models.CharField(default='SOME STRING', max_length=140),
        ),
    ]
