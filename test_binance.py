import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
testnet = os.getenv("BINANCE_TESTNET", "true").lower() == "true"

print(f"Testing Binance Connectivity (Testnet: {testnet})...")
try:
    client = Client(api_key, api_secret, testnet=testnet)
    account = client.get_account()
    print("✅ Success! Account connected.")
    print(f"Account Permissions: {account.get('permissions', [])}")
    for balance in account.get('balances', []):
        if float(balance['free']) > 0:
            print(f"Asset: {balance['asset']}, Free: {balance['free']}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
