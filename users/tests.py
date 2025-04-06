from django.test import TestCase, Client
from django.db import connection
from .models import User
from rest_framework import status
import json

# User Details are been checked. If they exsit or not and checked all the edge cases.
class UserGetAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.urls = "/users/"

        # Clean up before inserting to avoid duplication
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM users WHERE "userID" = %s', [1])

            # Insert test user with correct column names
            cursor.execute("""
                INSERT INTO users ("userID", "FirstName", "LastName", "PhoneNumber", "DOB", "MailID", "Address", state)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                1, "John", "Doe", "9876543210", "2000-01-01",
                "john@example.com", "123 Street, City", "Karnataka"
            ])

    def test_valid_user(self):
        response = self.client.get(self.urls, {'id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['User']['FirstName'], "John")

    def test_user_not_found(self):
        response = self.client.get(self.urls, {'id': 999})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['Msg'], "User Not Found")

    def test_user_id_missing(self):
        response = self.client.get(self.urls)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['Msg'], "User ID not provided")

    def test_user_id_invalid(self):
        response = self.client.get(self.urls, {'id': 'abc'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['Msg'], "Invalid User ID")


# Inserting the User Data checking the API method
class InsertingUserApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.urls = "/users/create-user/"
        self.payload = {
            "FirstName": "Adithya",
            "LastName": "Sharma",
            "PhoneNumber": "9390030344",
            "DOB": "2004-06-18",
            "MailID": "AS@gmail.com",
            "Address": "Shivaji Nagar, Nizamabad",
            "state": "Nizamabad, Telagana"
        }
        User.objects.filter(PhoneNumber=self.payload["PhoneNumber"]).delete()

    def test_valid_user_Insertion(self):
        response = self.client.post(
            self.urls,
            data=json.dumps(self.payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['Msg'], 'User created successfully')

    def test_duplicate_user_Insertion(self):
        # First insertion
        self.client.post(
            self.urls,
            data=json.dumps(self.payload),
            content_type='application/json'
        )
        # Duplicate insertion
        response = self.client.post(
            self.urls,
            data=json.dumps(self.payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['Msg'], 'The data which you are trying to send is already exist')

    def test_missing_data(self):
        response = self.client.post(
            self.urls,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['Msg'], 'No data provided')

# Patch Work for this API to the user if want to change then he can change his details here.       
class PatchApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.payload = {
            "FirstName": "Priya",
            "LastName": "Sharma",
            "PhoneNumber": "9876543216",
            "DOB": "2000-12-05",
            "MailID": "PS@gmail.com",
            "Address": "Shivaji Nagar, Nizamabad",
            "state": "Nizamabad, Telagana"
        }
        self.user = User.objects.create(**self.payload)
        self.urls = f"/users/update-user/{self.user.userID}/"

    def test_patch_user_success_found(self):
        patch_payload = {
            "PhoneNumber": "8888888888",
            "Address": "kompally, Hyderabad"
        }
        
        json_data = json.dumps(patch_payload)
        
        response = self.client.generic(
            'PATCH',
            self.urls,
            data=json_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Msg"], "User data updated successfully")

    def test_patch_user_fail_to_found(self):
        invalid_url = "/users/update-user/99/"
        patch_payload = {
            "PhoneNumber": "1234567890"
        }
        
        json_data = json.dumps(patch_payload)
        
        response = self.client.generic(
            'PATCH',
            invalid_url,
            data=json_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["Msg"], "User not found")
        
    def test_patch_user_invalid_data(self):
        payload = {
            "randomfield": "somevalue"
        }
        response = self.client.patch(
            self.urls,
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["Msg"], "No valid fields provided for update")

    def test_patch_user_empty_data(self):
        response = self.client.patch(
            self.urls,
            data={},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.json()["Msg"], "No data provided")


