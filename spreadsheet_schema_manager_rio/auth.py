import os
import requests
from urllib.parse import urlencode

import rio

from . import data_models


# Keycloak OAuth settings
ISSUER = os.getenv('AUTH_ISSUER', 'https://keycloak.auth.k8s.pfr.co.nz/realms/PFR')
AUTHORIZATION_ENDPOINT = f"{ISSUER}/protocol/openid-connect/auth"
TOKEN_ENDPOINT = f"{ISSUER}/protocol/openid-connect/token"
USER_INFO_ENDPOINT = f"{ISSUER}/protocol/openid-connect/userinfo"
LOGOUT_ENDPOINT = f"{ISSUER}/protocol/openid-connect/logout"
SCOPE = "openid profile email"
CLIENT_ID = os.getenv('AUTH_CLIENT_ID', 'spreadsheet-schema')
CLIENT_SECRET = os.getenv('AUTH_SECRET_KEY')
REDIRECT_URI = os.getenv('AUTH_REDIRECT_URI')
CA_CERT_PATH = os.getenv('REQUESTS_CA_BUNDLE')

# Shown on the login button, e.g. "Log in via {AUTH_PROVIDER_LABEL} SSO".
AUTH_PROVIDER_LABEL = os.getenv('AUTH_PROVIDER_LABEL', 'PFR')

# When set, Keycloak login is bypassed. Each new session is attached its
# own fresh synthetic AppUser (a new ObjectId every time) - it's never
# looked up by name/email or persisted to the `users` collection, just
# used to scope ownership of whatever Fields/Templates/Workbooks that
# session creates. This is intentional, not a gap to fix: it gives every
# browser session/test run its own clean, isolated "personal space" with
# no cross-test data leakage and no need for explicit cleanup between
# runs. Must only ever be enabled in UAT, to let tests drive the app
# without going through the SSO flow.
AUTH_DISABLED = os.getenv('AUTH_DISABLED', 'false').strip().lower() == 'true'
TEST_USER_NAME = os.getenv('TEST_USER_NAME')
TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL')


def get_authorization_url() -> str:
    query_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
    }
    return f"{AUTHORIZATION_ENDPOINT}?{urlencode(query_params)}"


def get_access_token(auth_code: str) -> str:
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_ENDPOINT, data=payload, verify=CA_CERT_PATH)
    response.raise_for_status()
    return response.json().get("access_token")


def fetch_user_info(access_token: str) -> dict | None:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(USER_INFO_ENDPOINT, headers=headers, verify=CA_CERT_PATH)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch user info:", response.status_code, response.text)
        return None


def logout() -> None:
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(LOGOUT_ENDPOINT, data=payload, verify=CA_CERT_PATH)


def guard(event: rio.GuardEvent) -> str | None:
    if AUTH_DISABLED:
        try:
            event.session[data_models.AppUser]
        except KeyError:
            event.session.attach(
                data_models.AppUser.new(
                    name=TEST_USER_NAME,
                    email=TEST_USER_EMAIL,
                )
            )
        return None

    try:
        event.session[data_models.AppUser]
    except KeyError:
        return "/login"

    return None
