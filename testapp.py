import requests
import json

BASE_URL = "http://localhost:8000"  # Adjust this to your actual API base URL

def print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("---")

def register_user(username, email, password):
    response = requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    print(f"Registered user {username}")
    print_response(response)
    return response.json()

def login_user(username, password):
    response = requests.post(f"{BASE_URL}/users/login", data={
        "username": username,
        "password": password
    })
    print(f"Logged in user {username}")
    print_response(response)
    return response.json()["access_token"]

def create_group(token, group_name):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/groups/", headers=headers, json={
        "name": group_name
    })
    print(f"Created group {group_name}")
    print_response(response)
    return response.json()["id"]

def add_member_to_group(token, group_id, username):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/groups/{group_id}/members/{username}", headers=headers)
    print(f"Added {username} to group {group_id}")
    print_response(response)

def create_expense(token, group_id, description, amount, paid_by, split_type, split_details):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/expenses/", headers=headers, json={
        "group_id": group_id,
        "description": description,
        "amount": amount,
        "paid_by": paid_by,
        "split_type": split_type,
        "split_details": split_details
    })
    print(f"Created expense: {description}")
    print_response(response)
    return response.json()["id"]

def get_group_expenses(token, group_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/expenses/{group_id}", headers=headers)
    print(f"Got expenses for group {group_id}")
    print_response(response)
    return response.json()

def get_group_balances(token, group_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/expenses/{group_id}/balances", headers=headers)
    print(f"Got balances for group {group_id}")
    print_response(response)
    return response.json()

def settle_group_debts(token, group_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/expenses/{group_id}/settle", headers=headers)
    print(f"Settled debts for group {group_id}")
    print_response(response)
    return response.json()

# Main test script
def run_test():
    # Register users
    register_user("alice", "alice@example.com", "password123")
    register_user("bob", "bob@example.com", "password456")
    register_user("carol", "carol@example.com", "password789")

    # Login users
    alice_token = login_user("alice", "password123")
    bob_token = login_user("bob", "password456")
    carol_token = login_user("carol", "password789")

    # Create a group
    group_id = create_group(alice_token, "Summer Vacation 2024")

    # Add members to the group
    add_member_to_group(alice_token, group_id, "bob")
    add_member_to_group(alice_token, group_id, "carol")

    # Create expenses
    create_expense(alice_token, group_id, "Flight Tickets", 600, "alice", "equal", 
                   {"alice": 1, "bob": 1, "carol": 1})
    create_expense(bob_token, group_id, "Hotel Booking", 900, "bob", "percentage", 
                   {"alice": 40, "bob": 40, "carol": 20})
    create_expense(carol_token, group_id, "Dinner", 150, "carol", "fixed", 
                   {"alice": 50, "bob": 50, "carol": 50})

    # Get group expenses
    get_group_expenses(alice_token, group_id)

    # Get group balances
    get_group_balances(alice_token, group_id)

    # Settle group debts
    settle_group_debts(alice_token, group_id)

if __name__ == "__main__":
    run_test()