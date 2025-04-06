from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_accounttransaction_transactiontype'),  # Reference the previous migration
    ]

    operations = [
        migrations.RenameField(
            model_name='accounttransaction',
            old_name='accountnumber',  # Old field name
            new_name='account',  # New field name
        ),
    ]
