import asyncio
import argparse
import sys
from engine.clients.telegram import TelegramClient, TelegramAccountManager

# Mock config for verification script
# In real usage, this comes from ContextLoader
MOCK_CONFIG = {
    "api_id": None, # Will load from env
    "api_hash": None, # Will load from env
    "sessions_dir": "data/store/system/sessions",
    "db_path": "data/store/system/telegram_accounts.db"
}

async def main():
    parser = argparse.ArgumentParser(description="Verify Telegram Sending")
    parser.add_argument("--phone", help="Phone number to use (must be auth'd)")
    parser.add_argument("--to", default="me", help="Username or ID to send to (default: Saved Messages)")
    parser.add_argument("--msg", default="Hello from Antigravity!", help="Message content")
    args = parser.parse_args()

    # Find account
    manager = TelegramAccountManager(MOCK_CONFIG["db_path"])
    
    if args.phone:
        phone = args.phone
    else:
        # Auto-pick first active account
        accounts = manager.list_accounts(status="active")
        if not accounts:
            print("No active accounts found in DB. Please run telegram_auth.py first.")
            sys.exit(1)
        phone = accounts[0]["phone_number"]
        print(f"Auto-selected account: {phone}")

    client = TelegramClient(MOCK_CONFIG)
    
    try:
        await client.connect(phone)
        await client.send_message(args.to, args.msg)
        print(f"✅ Message sent to {args.to}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
