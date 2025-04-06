from django.shortcuts import render
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.timezone import now
import uuid , datetime
from users.models import User, AccountTransaction, AccountInfo

# ----------------------------- New Code  -----------------------------------

class PostApiView(APIView):
    def generate_utr(self):
        """Generate a unique transaction reference (UTR)"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = uuid.uuid4().hex[:8].upper()
        return f"{timestamp}{random_part}"

    def post(self, request):
        """Handles money transfer transactions"""
        data = request.data
        userID = data.get('userID')
        AccountNo = data.get('AccountNumber')
        MoneyTransferred = data.get('moneytransferred')  # ✅ Corrected spelling
        ReceiverName = data.get('receivername')
        ReceiverAccountNumber = data.get('receiveraccountnumber')
        ReceiverIFSCode = data.get('receiverifsccode')  # ✅ Matches model

        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT "userID" FROM "users" WHERE "userID" = %s', [userID])
                if not cursor.fetchone():
                    return Response({'Msg': 'User ID does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                cursor.execute("SELECT AccountNumber, CurrentBalance FROM account_info WHERE AccountNumber = %s", [AccountNo])
                row = cursor.fetchone()
                if not row:
                    return Response({'Msg': 'Invalid account number or balance unavailable'}, status=status.HTTP_400_BAD_REQUEST)
                
                db_account_no, db_current_bal = row
                if db_current_bal < MoneyTransferred:
                    return Response({'Msg': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

                new_balance = db_current_bal - MoneyTransferred
                UTR = self.generate_utr()

                cursor.execute(
                    """
                    INSERT INTO account_transaction (account_id, utr, currentbalance, dateoftransaction, 
                    receivername, receiveraccountnumber, receiverifsccode, moneytransferred, transactiontype, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [AccountNo, UTR, new_balance, datetime.datetime.now(), ReceiverName, ReceiverAccountNumber, ReceiverIFSCode, MoneyTransferred, 'Credit', 'processing']
                )
                cursor.execute("UPDATE account_info SET currentbalance = %s WHERE AccountNumber = %s", [new_balance, AccountNo])
                return Response({'Msg': 'Transaction initiated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'Msg': 'Transaction failed', 'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PatchApiView(APIView):
    def patch(self, request):
        """Updates the transaction status"""
        data = request.data
        utr = data.get("utr")
        status_update = data.get("status")

        if not utr or not status_update:
            return Response({'Msg': 'Missing UTR or status'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Allowed status values
        allowed_status = {"processing", "success", "failed", "pending"}
        if status_update.lower() not in allowed_status:
            return Response({'Msg': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE account_transaction SET status = %s WHERE utr = %s", [status_update.lower(), utr])
                
                # ✅ Check if any row was updated
                if cursor.rowcount == 0:
                    return Response({'Msg': 'UTR not found or no update needed'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'Msg': 'Transaction status updated'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Msg': 'Update failed', 'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetApiView(APIView):
    def get(self, request):
        """Retrieves transaction details by UTR or account number"""
        utr = request.query_params.get('utr')
        account_number = request.query_params.get('accountnumber')

        if not account_number:
            return Response({'Msg': 'Account number required'}, status=status.HTTP_400_BAD_REQUEST)

        query = "SELECT * FROM account_transaction WHERE accountnumber = %s"
        params = [account_number]

        if utr:
            query += " AND utr = %s"
            params.append(utr)

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()

                if not rows:
                    return Response({'Msg': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

                # ✅ Dynamically fetch column names to avoid index-based mapping
                columns = [col[0] for col in cursor.description]

                # ✅ Convert multiple rows into a structured response
                transactions = [dict(zip(columns, row)) for row in rows]

                return Response(transactions, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'Msg': 'Error retrieving transaction', 'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetAllTransactionsApiView(APIView):
    def get(self, request):
        """Retrieves all transactions for a given account number"""
        account_number = request.query_params.get('accountnumber')

        if not account_number:
            return Response({'Msg': 'Account number required'}, status=status.HTTP_400_BAD_REQUEST)

        query = """ 
        SELECT * FROM account_transaction 
        WHERE accountnumber = %s AND status IN ('Success', 'Failure', 'Processing') 
        """
        params = [account_number]

        try:
            with connection.cursor() as cursor: 
                cursor.execute(query, params)
                rows = cursor.fetchall()

                if not rows:
                    return Response({'Msg': 'No transaction details found'}, status=status.HTTP_404_NOT_FOUND)

                # ✅ Fetch column names dynamically to prevent index-based errors
                columns = [col[0] for col in cursor.description]

                # ✅ Convert query result to list of dictionaries
                transactions = [dict(zip(columns, row)) for row in rows]

                return Response(transactions, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'Msg': 'Error retrieving transactions', 'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# ----------------------------- OLD Code  -----------------------------------
# # Create your views here.

# class PostApiView(APIView):

#     # @ generated the UTR for ever transaction 
#     def generate_utr(self):
#         now = datetime.datetime.now()
#         timestamp = now.strftime('%Y%m%d%H%M%S')
#         random_part = uuid.uuid4().hex[:8].upper()  # 6-character random part
#         return  f"{timestamp}{random_part}"
    
    

#     def post(self , request):
    
#         #loading the details from the user

#         # ------ More use of TRY and CATCH --------
#         # @ Masking Errors: Can hide underlying issues, making debugging difficult.
#         # @ Performance Overhead: Introduces some performance cost.
#         # @ Complexity: Makes code harder to read and maintain.
#         # @ Improper Handling: Catching general exceptions can lead to poor error handling.
#         # @ Encourages Bad Practices: Can lead to poor coding practices like using it for flow control.

#         data = request.data
#         userID = data.get('userID')
#         AccountNo = data.get('AccountNumber')
#         Moneytransfered = data.get('moneytransferred')
#         ReciverName = data.get('receivername')
#         ReciverAccountNumber = data.get('receiveraccountnumber')
#         ReciverIFSCode = data.get('receiverifcscode')



#         #checking user exist or not
#         try:
#             with connection.cursor() as cursor: 

#                 # check if input user id is in the database or not 
#                 cursor.execute("SELECT * FROM users WHERE userID = %s", [userID])
#                 row = cursor.fetchone() # it will return tuple

#                 if row:
#                     db_user_id = row[0]
#                 else:
#                     db_user_id = None

                
#                 if db_user_id is None:
#                     return Response({'Msg': 'User ID does not exist'}, status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     # fetch account related details for the user
#                     # write the query to account_info table to fetch account_number 

#                     cursor.execute("select AccountNumber, CurrentBalance from account_info where AccountNumber = %s", [AccountNo])
#                     row1 = cursor.fetchone()
#                     if row1:
#                         db_account_no = row1[0]
#                         db_current_bal = row1[1]
#                     else:
#                         db_account_no = None
#                         db_current_bal = None

#                         # now chcek for two conditions
#                         # 1. if the current balance >= moneytraffered
#                         # 2. if the MT is > 0
                    
#                     # @ has been handled here
#                     if db_account_no is None or db_current_bal is None:
#                         return Response({'Msg': 'Please Check CurrentBalance or AccountNumber.'}, status=status.HTTP_400_BAD_REQUEST)
#                     else:
#                         if db_current_bal >= Moneytransfered:
#                             print(db_current_bal, type(db_current_bal), type(Moneytransfered))
#                             new_balance = db_current_bal - Moneytransfered 
#                             UTR = self.generate_utr()

#                             query = '''
#                                 INSERT INTO account_transaction (accountnumber,utr ,current_balance ,dateoftransaction ,receivername  ,receiveraccountnumber, receiverifcscode, moneytransfered, transactiontype, status)
#                                 VALUES (%s, %s, %s, %s ,%s, %s ,%s, %s ,%s, %s)
#                             '''
                           
#                             cursor.execute(query, [AccountNo, UTR , new_balance , now() , ReciverName , ReciverAccountNumber , ReciverIFSCode, Moneytransfered, 'Cred', 'processing']) 
#                             # every time the utr change because changed 

#                             Update_query = '''
#                             UPDATE account_info SET currentbalance = %s where accountnumber = %s
#                             '''

#                             cursor.execute(Update_query , [ new_balance , AccountNo])

#                             return Response({'Msg': 'Transaction initiated successfully, process is in progress'}, status=status.HTTP_200_OK)
#                         else:
#                             return Response({'Msg': 'Current balance is less than the transfer amount'}, status=status.HTTP_400_BAD_REQUEST)


#         except Exception as e:
#             return Response({'Msg': 'Transaction failed, please try again', 'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    

# # 1. utr is manual as of now use uuid to generate UTR (DONE)
# # 2. handle negitive senarios  (DONE)
# # 3. why should we not have amny try catches (DONE)
# # 4. updating the variables (DONE)

# # -------(DONE)-------
# # write a patch API for the transaction
# # 1. one thing we need to do is to update the status of the tranaction -> to success or to failure 
# # 2. if you are updating to failure should we need UTR ? so we need to update UTR to '' or None chcek what suits the best 
# # 4. if we are updating to success we only need to update status. 

# # as of now only do this and come to me 
# # how much time will you take ? 1.5 hrs from now 

# class PatchApiView(APIView):
#     def patch(self , request):

#         data = request.data
#         utr = data.get("utr")
#         Status = data.get("status")
#         transaction_flag= data.get("transaction_flag")


#         try:
#             if not data:
#                 return Response({'Msg': 'User Not given the data '}, status=status.HTTP_400_BAD_REQUEST)

#             if transaction_flag:
#                 Query = f"UPDATE account_transaction SET status = %s where utr = %s"

#                 with connection.cursor() as cursor:
#                     cursor.execute(Query, [Status , utr])

#                 return Response({'Msg':'Transaction status updated'},status=status.HTTP_200_OK )
#             else:
#                  return Response({'Msg': 'Please Transaction is not updated sucessfully '}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'Msg': 'User data has not been updated successfully' , 'Error' : str(e)}, status=status.HTTP_400_BAD_REQUEST)

# # ------ DONE ------
# # things to do 
# '''
# 1. write a get API to fetch tranaction details input : UTR 
# 2. input : account_number 
# 3 . code wil be full stoped 
# '''

# # Full decusion of the project 

# # total SQL every minute detail (query part is ****) days :- (2 weeks + 1 extra). 

# # what is the purpose of the project ....... 
# # Total report of the porject 
# # DSA compalsory 


# class GetApiView(APIView):
#     def get(self , request):
#         UTR = request.query_params.get('utr')
#         AccountNumber = request.query_params.get('accountnumber')

#         # @1 getting the request from the API of UTR and AccNum

#         if not AccountNumber:
#             return Response({'Msg': 'AccountNumber not FOUND!!!'}, status=status.HTTP_404_BAD_REQUEST)

#         # @2 If the AccNum is not given then error for not given AccNum. 


#         if UTR:
#             query = " SELECT * FROM account_transaction WHERE accountnumber = %s and utr = %s and (status = 'Sucess'  or status = 'Failure') "
#             # accountnumber, 
#             # utr, 
#             # transactiontype, 
#             # moneytransfered, 
#             # current_balance, 
#             # dateoftransaction, 
#             # receivername, 
#             # receiveraccountnumber, 
#             # receiverifcscode, 
#             # status    
#             param = [AccountNumber , UTR]        
        
#         # @3 IF UTR gievn then check for the details of the user for that particular UTR. Getting the required details by both querys's

#         # else:
#         #     query = " SELECT * FROM account_transaction WHERE accountnumber = %s and utr = %s and status = 'Failure' "
            
#         #     # SELECT 
#         #     # accountnumber, 
#         #     # utr, 
#         #     # transactiontype, 
#         #     # moneytransfered, 
#         #     # current_balance, 
#         #     # dateoftransaction, 
#         #     # receivername, 
#         #     # receiveraccountnumber, 
#         #     # receiverifcscode, 
#         #     # status  
#         #     # FROM account_transaction WHERE accountnumber = %s and status = 'Failure' '''
#         #     param = [AccountNumber]
        
#         # @4 If UTR not given then check for the transaction where status is Failure.

#         with connection.cursor() as cursor: 
#             cursor.execute(query , param)
#             row = cursor.fetchone()
        
#         # @5 connecting with DB for getting the information of the query

#             if row:            
#                 Details = {
#                     "accountnumber" : row[0],
#                     "utr" : row[1],
#                     "transactiontype" : row[2],
#                     "moneytransfered" : row[3],
#                     "current_balance" : row[4],
#                     "dateoftransaction" : row[5],
#                     "receivername" : row[6],
#                     "receiveraccountnumber" : row[7],
#                     "receiverifcscode" : row[8],
#                     "status" : row[9]
#                 }

#                 return Response(Details, status=status.HTTP_200_OK)
#             else:
#                 return Response({'Msg': 'Transaction details are not found'}, status=status.HTTP_404_BAD_REQUEST)

#         # @6 If the row is not NONE then we are giving the details dict where we have to get all the required column of the particular transaction otherwise error.


# # ------- Getting all the transaction details of that particular Account by only AccNum from the user in the dict 
# class GETApiView(APIView):
#     def get(self , request):
#         AccountNumber = request.query_params.get('accountnumber')

#         if not AccountNumber:
#             return Response({'Msg': 'AccountNumber not FOUND!!!'}, status=status.HTTP_404_BAD_REQUEST)
#         else :
#             query = " SELECT * FROM account_transaction WHERE accountnumber = %s and (status = 'Sucess'  or status = 'Failure' or status = 'processing') "
#             # accountnumber, 
#             # utr, 
#             # transactiontype, 
#             # moneytransfered, 
#             # current_balance, 
#             # dateoftransaction, 
#             # receivername, 
#             # receiveraccountnumber, 
#             # receiverifcscode, 
#             # status    
#             param = [AccountNumber]  

        
#         with connection.cursor() as cursor: 
#             cursor.execute(query , param)
#             rows = cursor.fetchall()

#             if rows:
#                 AllTransactions = []            
#                 for row in rows:
#                     Details = {
#                     "accountnumber" : row[0],
#                     "utr" : row[1],
#                     "transactiontype" : row[2],
#                     "moneytransfered" : row[3],
#                     "current_balance" : row[4],
#                     "dateoftransaction" : row[5],
#                     "receivername" : row[6],
#                     "receiveraccountnumber" : row[7],
#                     "receiverifcscode" : row[8],
#                     "status" : row[9]
#                     }
#                     AllTransactions.append(Details)

#                 return Response(AllTransactions, status=status.HTTP_200_OK)
#             else:
#                 return Response({'Msg': 'Transaction details are not found'}, status=status.HTTP_404_BAD_REQUEST)