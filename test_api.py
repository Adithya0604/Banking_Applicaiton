import requests

# Base URL of your Django server
base_url = "http://127.0.0.1:8000"

# Test GET endpoint
def test_get_user(user_id=1):
    try:
        response = requests.get(f"{base_url}/users/?id={user_id}")
        print(f"GET /users/?id={user_id} Status: {response.status_code}")
        
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception occurred: {e}")
    
# Test POST endpoint
def test_create_user():
    try:
        data = {
            "FirstName": "Test",
            "LastName": "User",
            "PhoneNumber": "9876543215",
            "DOB": "1990-01-01",
            "MailID": "test@example.com",
            "Address": "789 Test Street, TestCity",
            "state": "Delhi"
        }
        response = requests.post(f"{base_url}/create-user/", json=data)
        print(f"POST /create-user/ Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(response.json())
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception occurred: {e}")

# Run tests
if __name__ == "__main__":
    print("Testing GET user endpoint:")
    test_get_user()
    
    print("\nTesting CREATE user endpoint:")
    test_create_user()