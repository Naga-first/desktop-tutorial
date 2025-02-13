import asyncio
import websockets
import json
import os

USER_CREDENTIALS_FILE = "users.json"

def load_users():
    if os.path.exists(USER_CREDENTIALS_FILE):
        with open(USER_CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USER_CREDENTIALS_FILE, 'w') as f:
        json.dump(users, f)

users = load_users()
clients = {} 

async def authenticate(websocket):
    await websocket.send("LOGIN or REGISTER?")
    choice = await websocket.recv()
    
    if choice.upper() == "REGISTER":
        await websocket.send("Enter a new username:")
        username = await websocket.recv()
        
        if username in users:
            await websocket.send("Username already exists. Try again.")
            return None
        else:
            await websocket.send("Enter a new password:")
            password = await websocket.recv()
            users[username] = password
            save_users(users)
            await websocket.send("Registration successful! Please login.")
            return await authenticate(websocket) 

    elif choice.upper() == "LOGIN":
        await websocket.send("Enter your username:")
        username = await websocket.recv()

        if username not in users:
            await websocket.send("Username not found. Try again.")
            return None

        await websocket.send("Enter your password:")
        password = await websocket.recv()

        if users[username] == password:
            await websocket.send("Login successful!")
            return username
        else:
            await websocket.send("Incorrect password. Try again.")
            return None
    else:
        await websocket.send("Invalid choice. Type LOGIN or REGISTER.")
        return None

async def broadcast(message, sender=None):
    for client in clients.values():
        if client != sender:
            try:
                await client.send(message)
            except:
                continue

async def handle_client(websocket, path):
    username = await authenticate(websocket)
    if not username:
        await websocket.close()
        return

    clients[username] = websocket
    await broadcast(f"{username} joined the chat!")

    try:
        async for message in websocket:
            if message.strip().upper() == "EXIT":
                break
            else:
                await broadcast(f"{username}: {message}", sender=websocket)
    except:
        pass
    finally:
        del clients[username]
        await broadcast(f"{username} has left the chat.")
        await websocket.close()

async def main():
    server = await websockets.serve(handle_client, "0.0.0.0", 55555)
    print("WebSocket server running on ws://0.0.0.0:55555")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
