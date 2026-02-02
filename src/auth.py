from py_clob_client.client import ClobClient
import os

# L1 wallet authentication
host = "https://clob.polymarket.com"
chain_id = 137 # Polygon mainnet
private_key = os.getenv("PRIVATE_KEY")

client = ClobClient(
    host=host,
    chain_id=chain_id,
    key=private_key  # Signer enables L1 methods
)

# Gets API key, or else creates
api_creds = await client.create_or_derive_api_key()

# api_creds = {
#     "apiKey": "550e8400-e29b-41d4-a716-446655440000",
#     "secret": "base64EncodedSecretString",
#     "passphrase": "randomPassphraseString"
# }

print(f"API credentials: \n{api_creds}")

# L2 wallet authentication

client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=137,
    key=os.getenv("PRIVATE_KEY"),
    creds=api_creds,  # Generated from L1 auth, API credentials enable L2 methods
    signature_type=1,  # signatureType explained below
    funder=os.getenv("FUNDER_ADDRESS") # funder explained below
)

# Now you can trade!*
order = await client.create_and_post_order(
    {"token_id": "123456", "price": 0.65, "size": 100, "side": "BUY"},
    {"tick_size": "0.01", "neg_risk": False}
)