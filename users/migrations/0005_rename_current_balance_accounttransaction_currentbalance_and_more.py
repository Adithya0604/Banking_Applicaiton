# Generated by Django 5.0.5 on 2025-04-06 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_rename_account_accounttransaction_accountnumber_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accounttransaction',
            old_name='current_balance',
            new_name='currentbalance',
        ),
        migrations.RenameField(
            model_name='accounttransaction',
            old_name='moneytransfered',
            new_name='moneytransferred',
        ),
        migrations.RenameField(
            model_name='accounttransaction',
            old_name='receiverifcscode',
            new_name='receiverifsccode',
        ),
        migrations.AlterField(
            model_name='user',
            name='FirstName',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='LastName',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='MailID',
            field=models.EmailField(blank=True, max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='PhoneNumber',
            field=models.CharField(max_length=15),
        ),
    ]
