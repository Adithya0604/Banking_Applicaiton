from django.shortcuts import render
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.timezone import now
from users.models import User, AccountTransaction, AccountInfo

# Create your views here.

class PostApiView(APIView):
    def post(self , request):
    
        #loading the details from the user
        try:
            data = request.data
            userID = data.get('userID')
            AccountNo = data.get('AccountNumber')
            Moneytransfered = data.get('moneytransferred')
                
        except (KeyError, ValueError):
            return Response({'Msg': 'Data not provided or invalid format', 'Error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


        #cheking user exist or not
        try:
            with connection.cursor() as cursor: 

                # check if input user id is in the database or not 
                cursor.execute("SELECT * FROM users WHERE userID = %s", [userID])
                row = cursor.fetchone() # it will return tuple

                if row:
                    db_user_id = row[0]
                else:
                    db_user_id = None

                
                if db_user_id is None:
                    return Response({'Msg': 'User ID does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # fetch account related details for the user
                    # write the query to account_info table to fetch account_number 

                    cursor.execute("select AccountNumber, CurrentBalance from account_info where AccountNumber = %s", [AccountNo])
                    row1 = cursor.fetchone()
                    if row1:
                        db_account_no = row1[0]
                        db_current_bal = row1[1]
                    else:
                        db_account_no = None
                        db_current_bal = None

                        # now chcek for two conditions
                        # 1. if the current balance >= moneytraffered
                        # 2. if the MT is > 0
                    
                    if db_account_no and db_current_bal:
                        if db_current_bal >= Moneytransfered:
                            new_balance = db_current_bal - Moneytransfered  

                            query = '''
                                INSERT INTO account_transaction (accountnumber,utr ,current_balance ,dateoftransaction ,receivername  ,receiveraccountnumber, receiverifcscode, moneytransfered, transactiontype, status)
                                VALUES (%s, %s, %s, %s ,%s, %s ,%s, %s ,%s, %s)
                            '''
                            cursor.execute(query, [AccountNo,'4160416041601' , new_balance , now() , data.get('ReciverName') , data.get('ReciverAccountNumber') , data.get('ReciverIFSCode'), Moneytransfered, 'Deb', 'processing']) 


                            return Response({'Msg': 'Transaction initiated successfully, process is in progress'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'Msg': 'Current balance is less than the transfer amount'}, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({'Msg': 'Transaction failed, please try again', 'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


                    #  if true
                    #  update current balance and use status as processing, 
                    #  insert the record into account transaction table. 
                    #  if inserted succesfully give the succes response to user saying process initiated. 
                    #  else transaction intiation failed. 


        # return Response({'Msg': 'Account information found'}, status=status.HTTP_200_OK)
    




        # if not User.objects.filter(userID=userID).exists():
        #     return Response({'Msg': 'User ID does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     # If user exist check account number exist or not
        #     try:
        #         account_info = AccountInfo.objects.get(userID=userID , AccountNumber=account_no)
        #     except AccountInfo.DoesNotExist:
        #         return Response({'Msg': 'Account information not found for the user'}, status=status.HTTP_400_BAD_REQUEST)

        # An user can have many accounts so check which account 
        # for account_info in accounts_info:
        #     if account_info.AccountNumber == AccountNo:
        #         flag = True
        #         # account number matching & checking Money transfer == 0 or not.
        #         if flag:
        #             if not Moneytransfered or Moneytransfered <= 0 :
        #                 return Response({'Msg':'Please transfer money first!!!' , status:status.HTTP_400_BAD_REQUEST})
        #         else:
        #             # Money transfer != 0. CB check with MT. CB < MT not valid.
        #             try:
        #                 if currentbalance < Moneytransfered:
        #                     return Response({'Msg':'Current Balance is less!!!' , status:status.HTTP_400_BAD_REQUEST})
        #                 else:
        #                     # CB >= MT. transfer the money and update the CB and save the details in Transaction table
        #                     currentbalance = currentbalance - Moneytransfered
        #                     AccountTransaction.save()
        #             # handling concurrent transaction issues
        #             except django.db.StaleObjectUpdate: 
        #                 return Response({'Msg': 'Concurrent transaction occurred, please try again'}, status=status.HTTP_409_CONFLICT)
        #     else:
        #         return Response({'Msg': 'Account number is not valid'}, status=status.HTTP_400_BAD_REQUEST)
