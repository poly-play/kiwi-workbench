
import os
import sys
import asyncio
import argparse
import yaml
from telethon import TelegramClient
from engine.clients.telegram import TelegramAccountManager
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError

# Load Taxonomy
TAXONOMY_PATH = "knowledge/domains/operations/telegram_taxonomy.yaml"

def load_taxonomy():
    if not os.path.exists(TAXONOMY_PATH):
        print(f"[Warn] Taxonomy file not found at {TAXONOMY_PATH}. Using generic fallback.")
        return None
    with open(TAXONOMY_PATH, 'r') as f:
        return yaml.safe_load(f)

def interactive_tag_selection():
    data = load_taxonomy()
    if not data:
        return prompt("Enter tags (comma separated): ")
    
    selected_tags = []
    
    # 1. Role (Multi Select)
    print("\n[?] Select Roles (optional, enter to skip):")
    roles = [r['id'] for r in data.get('roles', [])]
    role_completer = WordCompleter(roles)
    
    while True:
        r_input = prompt(f"Role ({'/'.join(roles)}): ", completer=role_completer).strip()
        if not r_input:
            break
        if r_input in roles:
            tag = f"role:{r_input}"
            if tag not in selected_tags:
                selected_tags.append(tag)
                print(f"Added {tag}")
        else:
            print("Invalid role.")

    # 2. Domain (Multi Select)
    print("\n[?] Select Business Domains (optional, enter to skip):")
    domains = [d['id'] for d in data.get('domains', [])]
    domain_completer = WordCompleter(domains)
    
    while True:
        d_input = prompt(f"Domain ({'/'.join(domains)}): ", completer=domain_completer).strip()
        if not d_input:
            break
        if d_input in domains:
            tag = f"domain:{d_input}"
            if tag not in selected_tags:
                selected_tags.append(tag)
                print(f"Added {tag}")
        else:
            print("Invalid domain.")

    # 3. Region (Multi Select)
    print("\n[?] Select Regions (optional, enter to skip):")
    regions = [r['id'] for r in data.get('regions', [])]
    region_completer = WordCompleter(regions)
    
    while True:
        r_input = prompt(f"Region ({'/'.join(regions)}): ", completer=region_completer).strip()
        if not r_input:
            break
        if r_input in regions:
            tag = f"region:{r_input}"
            if tag not in selected_tags:
                selected_tags.append(tag)
                print(f"Added {tag}")
        else:
            print("Invalid region.")
            
    return ",".join(selected_tags)

async def main():
    parser = argparse.ArgumentParser(description="Telegram Interactive Login & Registration")
    parser.add_argument("--phone", required=True, help="Phone number (international format)")
    parser.add_argument("--tags", help="Pre-defined tags (comma separated) to skip interactive selection")
    parser.add_argument("--app", default="global_ops", help="Virtual App Context (default: global_ops)")
    
    args = parser.parse_args()
    
    # Check Env
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print("Error: TELEGRAM_API_ID or TELEGRAM_API_HASH not found in .env")
        return

    # Tag Selection
    if args.tags:
        print(f"--- 🏷️ Using Pre-defined Tags: [{args.tags}] ---")
        final_tags = args.tags
    else:
        # Interactive Taxonomy Selection
        print("--- 🏷️ Account Tagging ---")
        final_tags = interactive_tag_selection()
    print(f"--- Final Tags: [{final_tags}] ---\n")

    # Session Path
    # Enforce isolation?
    # Actually, sessions are System Level Assets (global) or App Level?
    # Recommendation: Sessions are global resources used by Apps.
    # Keep sessions in data/sessions (gitignored).
    
    sessions_dir = "data/store/system/sessions"
    os.makedirs(sessions_dir, exist_ok=True)
    safe_phone = args.phone.replace("+", "")
    session_path = os.path.join(sessions_dir, safe_phone) 
    
    print(f"Starting auth for {args.phone}...")
    client = TelegramClient(session_path, int(api_id), api_hash)
    
    await client.start(phone=args.phone)
    
    print("Login successful!")
    me = await client.get_me()
    print(f"Authenticated as: {me.first_name} (ID: {me.id})")
    
    # Capture Account Name
    account_name = f"{me.first_name} {me.last_name}" if me.last_name else me.first_name
    
    await client.disconnect()
    
    # Register in DB
    # We should update AccountManager to accept app_context if needed, 
    # but for now accounts are global resources.
    manager = TelegramAccountManager()
    manager.add_account(args.phone, session_path, final_tags, account_name=account_name)
    
    print(f"Account registered in DB: {account_name} | Tags: {final_tags}")

if __name__ == "__main__":
    asyncio.run(main())
