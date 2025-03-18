import asyncio
import sys
from pathlib import Path

# Add the project directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.user_service import (
    create_user,
    get_user,
    list_users,
    update_user,
    delete_user
)
from dependencies.auth import keycloak_admin

async def setup():
    # Setup: Clear the users collection before each test
    try:
        users = keycloak_admin.get_users()
        for user in users:
            keycloak_admin.delete_user(user['id'])
        print("Setup: Cleared the users collection")
    except Exception as e:
        print(f"Setup failed: {str(e)}")

async def teardown():
    # Teardown: Clear the users collection after each test
    try:
        users = keycloak_admin.get_users()
        for user in users:
            keycloak_admin.delete_user(user['id'])
        print("Teardown: Cleared the users collection")
    except Exception as e:
        print(f"Teardown failed: {str(e)}")

async def test_create_user():
    user_data = {
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User",
        "enabled": True
    }
    created_user = await create_user(user_data)
    print(f"Created user: {created_user}")
    assert created_user["username"] == "testuser@example.com", f"Expected username 'testuser@example.com', got {created_user['username']}"
    print("test_create_user: Passed")

async def test_get_user():
    user_data = {
        "email": "testuser2@example.com",
        "firstName": "Test",
        "lastName": "User",
        "enabled": True
    }
    created_user = await create_user(user_data)
    user_id = created_user["id"]
    retrieved_user = await get_user(user_id)
    print(f"Retrieved user: {retrieved_user}")
    assert retrieved_user["username"] == "testuser2@example.com", f"Expected username 'testuser2@example.com', got {retrieved_user['username']}"
    print("test_get_user: Passed")

async def test_list_users():
    user_data_1 = {
        "email": "testuser3@example.com",
        "firstName": "Test",
        "lastName": "User",
        "enabled": True
    }
    user_data_2 = {
        "email": "testuser4@example.com",
        "firstName": "Test",
        "lastName": "User",
        "enabled": True
    }

    await create_user(user_data_1)
    await create_user(user_data_2)
    users = await list_users()
    print(f"List of users: {users}")
    assert len(users) == 2, f"Expected 2 users, got {len(users)}"
    assert users[0]["username"] == "testuser3@example.com", f"Expected username 'testuser3@example.com', got {users[0]['username']}"
    assert users[1]["username"] == "testuser4@example.com", f"Expected username 'testuser4@example.com', got {users[1]['username']}"
    print("test_list_users: Passed")

async def test_update_user():
    user_data = {
        "email": "testuser5@example.com",
        "firstName": "Test",
        "lastName": "User",
        "enabled": True
    }
    created_user = await create_user(user_data)
    user_id = created_user["id"]
    updated_user_data = {
        "email": "updateduser@example.com",
        "firstName": "Updated",
        "lastName": "User",
        "enabled": True
    }
    updated_user = await update_user(user_id, updated_user_data)
    print(f"Updated user: {updated_user}")
    assert updated_user["username"] == "updateduser@example.com", f"Expected username 'updateduser@example.com', got {updated_user['username']}"
    print("test_update_user: Passed")

async def test_delete_user():
    user_data = {
        "email": "testuser6@example.com",
        "firstName": "Test",
        "lastName": "User",
        "enabled": True
    }
    created_user = await create_user(user_data)
    user_id = created_user["id"]
    deleted_user = await delete_user(user_id)
    print(f"Deleted user: {deleted_user}")
    assert deleted_user["username"] == "testuser6@example.com", f"Expected username 'testuser6@example.com', got {deleted_user['username']}"
    print("test_delete_user: Passed")

async def main():
    await setup()
    try:
        await test_create_user()
        await test_get_user()
        #await test_list_users()
        await test_update_user()
        await test_delete_user()
    finally:
        await teardown()

if __name__ == "__main__":
    asyncio.run(main())