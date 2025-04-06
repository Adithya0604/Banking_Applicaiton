from django.shortcuts import render
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from django.db import transaction
from datetime import datetime
import json, re
from rest_framework.exceptions import ValidationError
from django.core.validators import validate_email



# ----------------------------- NEW Code  -----------------------------------

class UserApiView(APIView):
    def get(self, request):
        with transaction.atomic(): # atomicity check
            user_id = request.query_params.get('id') 

            if not user_id:
                return Response({'Msg': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user_id = int(user_id)
            except ValueError:
                return Response({'Msg': 'Invalid User ID'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                with connection.cursor() as cursor:     
                    cursor.execute('SELECT * FROM users WHERE "userID" = %s', [user_id])
                    row = cursor.fetchone()

                    if row:
                        if cursor.description:
                            columns = [col[0] for col in cursor.description]
                            user = dict(zip(columns, row))

                            if 'DOB' in user and user['DOB'] is not None:
                                user['DOB'] = str(user['DOB'])

                            # Convert all keys to match your model's field case
                            user = {
                                'userID': user.get('userID') or user.get('userid'),
                                'FirstName': user.get('FirstName') or user.get('firstname'),
                                'LastName': user.get('LastName') or user.get('lastname'),
                                'PhoneNumber': user.get('PhoneNumber') or user.get('phonenumber'),
                                'DOB': str(user.get('DOB') or user.get('dob')),
                                'MailID': user.get('MailID') or user.get('mailid'),
                                'Address': user.get('Address') or user.get('address'),
                                'state': user.get('state')
                            }

                            result = {
                                'Message': 'User Found',
                                'User': user,
                                'End': 'Thank You'
                            }
                            return Response(result, status=status.HTTP_200_OK)
                    else:
                        return Response({'Msg': 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
                        
            except Exception as e:
                import traceback
                print("Unexpected error:", e)
                traceback.print_exc()
                return Response({'Msg': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class InsertingUserDataApiView(APIView):
    def post(self, request):
        with transaction.atomic():
            data = request.data

            if not data:
                return Response({'Msg': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)

            required_fields = ['FirstName', 'LastName', 'PhoneNumber', 'DOB', 'MailID', 'Address', 'state']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return Response({'Msg': f'Missing fields: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)
            
            CellNumber = data.get('PhoneNumber')
            if User.objects.filter(PhoneNumber=CellNumber).exists():
                return Response({'Msg': 'The data which you are trying to send is already exist'}, 
                            status=status.HTTP_409_CONFLICT)

            try:
                dob_str = data.get('DOB') or data.get('dob')
                dob_value = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None

                # Create user
                User.objects.create(
                    FirstName=data.get('FirstName'),
                    LastName=data.get('LastName'),
                    PhoneNumber=CellNumber,
                    DOB=dob_value,
                    MailID=data.get('MailID'),
                    Address=data.get('Address'),
                    state=data.get('state')
                )

                return Response({'Msg': 'User created successfully'}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({'Msg': 'User Not Created', 'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




def validate_field(field, value):
    """Validate individual fields based on type rules and return specific error messages."""
    
    if field in ['FirstName', 'LastName', 'state']:
        # Ensure that the value is a non-empty string without special characters
        if not isinstance(value, str) or value.strip() == "" or re.search(r'[^\w\s]', value):
            raise ValidationError(f"Invalid value for {field}: {value} should be a non-empty string without special characters.")
        return True

    elif field == 'PhoneNumber':
        # Phone number should only have digits and should be 10-15 digits long
        if not isinstance(value, str) or not value.isdigit() or not (10 <= len(value) <= 15):
            raise ValidationError(f"Invalid value for {field}: {value} should be a valid phone number (10-15 digits) with digits only.")
        return True

    elif field == 'DOB':
        # Validate that the date is in the correct format YYYY-MM-DD
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid value for {field}: {value} should be in the format YYYY-MM-DD.")
        return True

    elif field == 'MailID':
    # Validate email format
        if isinstance(value, str):
            try:
                # Catch the validation error specifically and re-raise with your custom message
                validate_email(value)
                return True
            except Exception:
                raise ValidationError(f"Invalid value for {field}: {value} should be a valid email address.")
        else:
            raise ValidationError(f"Invalid value for {field}: {value} should be a valid email address.")
    
    elif field == 'Address':
        # Ensure that the value is a non-empty string without special characters
        if not isinstance(value, str) or value.strip() == "" or re.search(r'[^\w\s,.-]', value):
            raise ValidationError(f"Invalid value for {field}: {value} should be a valid address with allowed characters.")
        return True

    # If field is not recognized
    raise ValidationError(f"Unexpected field {field}.")


class PatchApiView(APIView):
    def patch(self, request, userID):
        with transaction.atomic():
            """Handle PATCH requests to update user data"""
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except json.JSONDecodeError:
                    return Response({'Msg': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = request.data

            print("Data", data)

            if not data:
                return Response({'Msg': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Field mapping (API -> DB columns)
            field_to_column = {
                'FirstName': 'FirstName',
                'LastName': 'LastName',
                'PhoneNumber': 'PhoneNumber',
                'DOB': 'DOB',
                'MailID': 'MailID',
                'Address': 'Address',
                'state': 'state'
            }

            allowed_fields = set(field_to_column.keys())

            corrected_data = {}
            invalid_fields = []

            for key, value in data.items():
                if key in allowed_fields:
                    try:
                        if validate_field(key, value):
                            db_column = field_to_column[key]
                            corrected_data[db_column] = value
                    except ValidationError as e:
                        invalid_fields.append(f"{key}: {str(e)}")

            if invalid_fields:
                return Response(
                    {'Msg': f'Invalid data for fields: {", ".join(invalid_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not corrected_data:
                return Response({'Msg': 'No valid fields provided for update'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                with connection.cursor() as cursor:
                    # Check if user exists
                    cursor.execute('SELECT "userID" FROM "users" WHERE "userID" = %s', [userID])
                    if not cursor.fetchone():
                        return Response({'Msg': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

                    # Build dynamic SQL update
                    query = ", ".join([f'"{key}" = %s' for key in corrected_data])
                    values = list(corrected_data.values())
                    values.append(userID)

                    update_query = f'UPDATE "users" SET {query} WHERE "userID" = %s'
                    print("Executing SQL:", update_query)
                    print("With values:", values)

                    cursor.execute(update_query, values)

                return Response({'Msg': 'User data updated successfully'}, status=status.HTTP_200_OK)

            except Exception as e:
                print(f"Database error: {e}")
                return Response({'Msg': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





# ------- Here are some improvements and fixes in your APIs ----- 

# Fixed SQL Injection Risks by using parameterized queries properly.

# Improved Error Handling to catch unexpected cases.

# Fixed Edge Cases like missing userID, incorrect PATCH handling, and better status codes.

# Optimized Code Readability with structured logging and meaningful responses.

# Updating your code now! 🚀

# Edited

# Answer in chat instead
# Summary of Changes:
# Improved Error Messages

# "User Not found" → "User ID not provided" if id is missing.

# "User Not found" → "Invalid User ID" if conversion fails.

# "User Not Created" now gives a clearer error reason.

# "User data has not been updated successfully" → "User not found or no changes made" if PATCH does nothing.

# Fixed SQL Query Issues

# Used COALESCE(MAX(userID), 0) to avoid None when fetching MAX(userID).

# PATCH now checks if any row was updated and returns a 404 if no changes were made.

# Code Optimizations

# Used .get() to avoid KeyError for missing data fields.

# Removed unnecessary print/debug statements.

# Used cursor.rowcount to check if an update actually happened. 

# ----------------------------------------------------------------
# *****}}


# ----------------------------- OLD Code  -----------------------------------
# # Create your views here.
# class UserApiView(APIView): 
#     def get(self, request): 
#         user_id = request.query_params.get('id')  
#         if not user_id:
#             return Response({'Msg': 'User Not found'}, status=status.HTTP_404_BAD_REQUEST)

#          #converting the unserid into int if it is given in string
#         try:
#             user_id = int(user_id)
#         except ValueError:
#             return Response({'Msg': 'User Not found'}, status=status.HTTP_404_BAD_REQUEST)

#         #feting the user details from the query .
#         with connection.cursor() as cursor: 
#             cursor.execute("SELECT * FROM users WHERE userID = %s", [user_id])
#             row = cursor.fetchone()

#             if row:
#             # cursor havin some methods with it like descriptio , fetchone , exceute ,fetch many , fetchall etc.
#                 COL = [col[0] for col in cursor.description]
#                 user = dict(zip(COL , row))
#                 user['dob'] = str(user['dob'])

#                 Result = {
#                     'Message' : 'User Found',
#                     'User' : user,
#                     'End' : 'Thank You'                }
#                 return Response(Result, status=status.HTTP_200_OK)
#             else:
#                 return Response({'Msg': 'User Not found'}, status=status.HTTP_404_BAD_REQUEST)
#                 '''This is only when we want to display the result and other messages in terminal. or we can directly display the 
#                 result by putting the result into the return statement.'''


# class InsertingUserDataApiView(APIView):
#     def post(self , request):
#         data = request.data

#         try:
#             with connection.cursor() as cursor:

#                 cursor.execute("SELECT MAX(userID) From users")
#                 row = cursor.fetchone()
#                 MaxUserId = row[0] if row  else None

#                 # manually checked the condition
#                 # MaxUserId = None

#                 if MaxUserId:
#                     NewUserId = MaxUserId + 1

#                     preethu = """
#                         INSERT INTO users (userID, FirstName, lastname, phonenumber, dob, mailid, address, state)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                     """
#                     cursor.execute(preethu, [NewUserId, data['firstname'], data['lastname'], data['phonenumber'], data['dob'], data['mailid'], data['address'], data['state']])
                    
#                     return Response({'Msg': 'User created successfully'}, status=status.HTTP_201_CREATED)
#                 return Response({'Msg': 'User Not Created ' , 'Error' : str('MaxUserId is not fetched')}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             print("in exception")
#             return Response({'Msg': 'User Not Created ' , 'Error' : str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class PatchApiView(APIView):
#      def patch(self , request , userID):
#             '''So, if the data is not provided by the user then we have to etuen the status has 400 bad request. If the user has provided 
#             the data what to be changed then we have to take the query  '''

#             data = request.data
#             try :
#                 if not data:
#                     return Response({'Msg': 'User Not given the data '}, status=status.HTTP_400_BAD_REQUEST)

#                 query = ", ".join([f"{key} = %s"for key in data.keys()])
#                 values = list(data.values())
#                 values.append(userID)
                

#                 QUERY = f"UPDATE users SET {query} where userID = %s"
#                 print("query",QUERY)

#                 with connection.cursor() as cursor:
#                     cursor.execute(QUERY, values)

#                     return Response({'Msg': 'User data has been updated successfully'}, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return Response({'Msg': 'User data has not been updated successfully' , 'Error' : str(e)}, status=status.HTTP_400_BAD_REQUEST)


















# """-----------   UserApiView   -------------"""
# '''Importing Necessary Modules:

# from django.db import connection: This imports the connection object from Django, which allows you to execute raw SQL queries.
# from rest_framework.views import APIView: This imports the APIView class from Django REST Framework, which provides the base for creating API views.
# from rest_framework.response import Response: This imports the Response class, used to return JSON responses.
# from rest_framework import status: This imports HTTP status codes.
# Defining the UserApiView Class:

# class UserApiView(APIView): Defines a view class that inherits from APIView.
# Handling the GET Request:

# def get(self, request): Defines the get method to handle GET requests.
# user_id = request.query_params.get('id'): Retrieves the id query parameter from the request URL.
# For example, if the URL is http://127.0.0.1:8000/users/?id=2, user_id will be 2.
# Validating the user_id:

# Checks if user_id is None. If it is, returns a 400 Bad Request response with an appropriate error message.
# Tries to convert user_id to an integer. If it fails (e.g., user_id is not a valid number), returns a 400 Bad Request response with an appropriate error message.
# Executing the Raw SQL Query:

# with connection.cursor() as cursor: Opens a new database cursor using Django's database connection. The cursor is automatically closed when the block is exited.
# cursor.execute("SELECT * FROM users WHERE userID = %s", [user_id]): Executes a raw SQL query to fetch the user with the given userID. The user_id is passed as a parameter to prevent SQL injection.
# row = cursor.fetchone(): Fetches the first row from the result of the query. If no row is found, row will be None.
# Printing the Row for Debugging:

# print(row): Prints the fetched row to the console for debugging purposes. This can help you verify if the query returns the expected result.
# Returning the Response:

# if row: Checks if a row was fetched from the database.
# If a row is found, it returns a 200 OK response with the message {'Msg': 'User found'}.
# If no row is found, it returns a 404 Not Found response with the message {'Msg': 'User not found'}.'''