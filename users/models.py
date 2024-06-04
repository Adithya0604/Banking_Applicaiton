from django.db import models


class User(models.Model):
    userID = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=200)
    LastName = models.CharField(max_length=200, blank=True, null=True)
    PhoneNumber = models.CharField(max_length=100)
    DOB = models.DateField()
    MailID = models.EmailField(max_length=200, blank=True, null=True)
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
    account = models.ForeignKey(AccountInfo, on_delete=models.CASCADE)
    utr = models.CharField(max_length=22, primary_key=True)
    transactiontype = models.CharField(max_length=4)
    moneytransferred = models.IntegerField()
    currentbalance = models.IntegerField(blank=True, null=True)
    dateoftransaction = models.DateTimeField()
    receivername = models.CharField(max_length=200, blank=True, null=True)
    receiveraccountnumber = models.CharField(max_length=17)
    receiverifsccode = models.CharField(max_length=11)
    Status = models.CharField(max_length=80)
   

    class Meta:
        db_table = "account_transaction"
