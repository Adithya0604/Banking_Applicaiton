from django.shortcuts import render
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User


# Create your views here.
class UserApiView(APIView): 
    def get(self, request): 
        user_id = request.query_params.get('id')  
        if not user_id:
            return Response({'Msg': 'User Not found'}, status=status.HTTP_404_BAD_REQUEST)

         #converting the unserid into int if it is given in string
        try:
            user_id = int(user_id)
        except ValueError:
            return Response({'Msg': 'User Not found'}, status=status.HTTP_404_BAD_REQUEST)

        #feting the user details from the query .
        with connection.cursor() as cursor: 
            cursor.execute("SELECT * FROM users WHERE userID = %s", [user_id])
            row = cursor.fetchone()

            if row:
            # cursor havin some methods with it like descriptio , fetchone , exceute ,fetch many , fetchall etc.
                COL = [col[0] for col in cursor.description]
                user = dict(zip(COL , row))
                user['dob'] = str(user['dob'])

                Result = {
                    'Message' : 'User Found',
                    'User' : user,
                    'End' : 'Thank You'                }
                return Response(Result, status=status.HTTP_200_OK)
            else:
                return Response({'Msg': 'User Not found'}, status=status.HTTP_404_BAD_REQUEST)
                '''This is only when we want to display the result and other messages in terminal. or we can directly display the 
                result by putting the result into the return statement.'''


class InsertingUserDataApiView(APIView):
    def post(self , request):
        data = request.data

        try:
            with connection.cursor() as cursor:

                cursor.execute("SELECT MAX(userID) From users")
                row = cursor.fetchone()
                MaxUserId = row[0] if row  else None

                # manually checked the condition
                # MaxUserId = None

                if MaxUserId:
                    NewUserId = MaxUserId + 1

                    preethu = """
                        INSERT INTO users (userID, FirstName, lastname, phonenumber, dob, mailid, address, state)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(preethu, [NewUserId, data['firstname'], data['lastname'], data['phonenumber'], data['dob'], data['mailid'], data['address'], data['state']])
                    
                    return Response({'Msg': 'User created successfully'}, status=status.HTTP_201_CREATED)
                return Response({'Msg': 'User Not Created ' , 'Error' : str('MaxUserId is not fetched')}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("in exception")
            return Response({'Msg': 'User Not Created ' , 'Error' : str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PatchApiView(APIView):
     def patch(self , request , userID):
            '''So, if the data is not provided by the user then we have to etuen the status has 400 bad request. If the user has provided 
            the data what to be changed then we have to take the query  '''

            data = request.data
            print("1")
            try :
                if not data:
                    return Response({'Msg': 'User Not given the data '}, status=status.HTTP_400_BAD_REQUEST)

                query = ", ".join([f"{key} = %s"for key in data.keys()])
                print("query", query)
                values = list(data.values())
                print("values",values)
                values.append(userID)
                

                QUERY = f"UPDATE users SET {query} where userID = %s"
                print("query",QUERY)

                with connection.cursor() as cursor:
                    cursor.execute(QUERY, values)

                    return Response({'Msg': 'User data has been updated successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'Msg': 'User data has not been updated successfully' , 'Error' : str(e)}, status=status.HTTP_400_BAD_REQUEST)


















"""-----------   UserApiView   -------------"""
'''Importing Necessary Modules:

from django.db import connection: This imports the connection object from Django, which allows you to execute raw SQL queries.
from rest_framework.views import APIView: This imports the APIView class from Django REST Framework, which provides the base for creating API views.
from rest_framework.response import Response: This imports the Response class, used to return JSON responses.
from rest_framework import status: This imports HTTP status codes.
Defining the UserApiView Class:

class UserApiView(APIView): Defines a view class that inherits from APIView.
Handling the GET Request:

def get(self, request): Defines the get method to handle GET requests.
user_id = request.query_params.get('id'): Retrieves the id query parameter from the request URL.
For example, if the URL is http://127.0.0.1:8000/users/?id=2, user_id will be 2.
Validating the user_id:

Checks if user_id is None. If it is, returns a 400 Bad Request response with an appropriate error message.
Tries to convert user_id to an integer. If it fails (e.g., user_id is not a valid number), returns a 400 Bad Request response with an appropriate error message.
Executing the Raw SQL Query:

with connection.cursor() as cursor: Opens a new database cursor using Django's database connection. The cursor is automatically closed when the block is exited.
cursor.execute("SELECT * FROM users WHERE userID = %s", [user_id]): Executes a raw SQL query to fetch the user with the given userID. The user_id is passed as a parameter to prevent SQL injection.
row = cursor.fetchone(): Fetches the first row from the result of the query. If no row is found, row will be None.
Printing the Row for Debugging:

print(row): Prints the fetched row to the console for debugging purposes. This can help you verify if the query returns the expected result.
Returning the Response:

if row: Checks if a row was fetched from the database.
If a row is found, it returns a 200 OK response with the message {'Msg': 'User found'}.
If no row is found, it returns a 404 Not Found response with the message {'Msg': 'User not found'}.'''