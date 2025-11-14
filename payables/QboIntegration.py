import requests
import json
import sys
import webbrowser
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

url = "https://sandbox-quickbooks.api.intuit.com"
redirect_uri = "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl"

client_id = "AB5eQHWb1e6raN97NnLM5NCxGJeQ9dDPnYhxAjQ5GJDHOvlH85"
client_secret = "9ktjvGn9yu30v3EW8yokq6wGkZtBtcyJAMKmnxdu"

auth_client = AuthClient(client_id, client_secret, redirect_uri, "sandbox")
url = auth_client.get_authorization_url([Scopes.ACCOUNTING])

r = requests.get(url=url, auth=(client_id, client_secret))
print(r.url)
