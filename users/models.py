from django.db import models


class User(models.Model):
    userID = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=50)
    LastName = models.CharField(max_length=50, blank=True, null=True)
    PhoneNumber = models.CharField(max_length=15) #changed the maxlenght to 15 from 100.
    DOB = models.DateField()
    MailID = models.EmailField(max_length=70, blank=True, null=True)
    Address = models.CharField(max_length=255)
    state = models.CharField(max_length=100)

    class Meta:
        db_table = "users"


class AccountInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    AccountNumber = models.CharField(max_length=17, primary_key=True)
    AccountType = models.CharField(max_length=100)
    CurrentBalance = models.IntegerField(blank=True, null=True)
    dateopened = models.DateTimeField()
    ifsccode = models.CharField(max_length=11)

    class Meta:
        db_table = "account_info"


class AccountTransaction(models.Model):
    utr = models.CharField(max_length=22, primary_key=True)  # Changed max_length from 50 to 22
    transactiontype = models.CharField(max_length=4)  # Changed max_length from 10 to 4
    moneytransferred = models.IntegerField(db_column='moneytransferred')  # Used original name with db_column
    currentbalance = models.IntegerField(blank=True, null=True, db_column='currentbalance')  # Restored original field name
    dateoftransaction = models.DateTimeField()
    receivername = models.CharField(max_length=200, blank=True, null=True)  # Added blank=True, null=True
    receiveraccountnumber = models.CharField(max_length=17)
    receiverifsccode = models.CharField(max_length=11, db_column='receiverifsccode')  # Used db_column for database column name
    Status = models.CharField(max_length=80)  # Changed max_length from 10 to 80
    accountnumber = models.ForeignKey(  # Changed field name from 'account' to 'accountnumber'
        AccountInfo, 
        on_delete=models.CASCADE, 
        to_field="AccountNumber",
        db_column='account_id'
    )



    class Meta:
        db_table = 'account_transaction'  # Ensures Django refers to the correct table

# class AccountTransaction(models.Model):
#     accountnumber = models.ForeignKey(AccountInfo, on_delete=models.CASCADE)
#     utr = models.CharField(max_length=22, primary_key=True)
#     transactiontype = models.CharField(max_length=4)
#     moneytransfered = models.IntegerField()
#     current_balance = models.IntegerField(blank=True, null=True)
#     dateoftransaction = models.DateTimeField()
#     receivername = models.CharField(max_length=200, blank=True, null=True)
#     receiveraccountnumber = models.CharField(max_length=17)
#     receiverifcscode = models.CharField(max_length=11)
#     Status = models.CharField(max_length=80)
   

#     class Meta:
#         db_table = "account_transaction"

