from os import environ as env
from urllib.parse import quote_plus, urlencode

import secrets
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import requests
from dotenv import load_dotenv

load_dotenv()

APP_SECRET_KEY = env.get("APP_SECRET_KEY")
APP_URL = env.get("APP_URL", "http://localhost:3000")
SCOPES = "offline_access openid profile email"

AUTH0_DOMAIN = env.get("AUTH0_DOMAIN")
MAIN_APP_URL = "https://" + AUTH0_DOMAIN
AUTH0_CLIENT_ID = env.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = env.get("AUTH0_CLIENT_SECRET")
AUTHORIZATION_URL = f"{MAIN_APP_URL}/authorize"
USERINFO_URL = f"{MAIN_APP_URL}/userinfo"
TOKEN_URL = f"{MAIN_APP_URL}/oauth/token"
LOGOUT_URL = f"{MAIN_APP_URL}/v2/logout"


app = FastAPI(title="Auth0 App")
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET_KEY, session_cookie="sessionid")


def exchange_code_for_token(code: str):
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"{APP_URL}/callback",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
        },
    )
    return response.json()


def get_userinfo(token: str):
    response = requests.get(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()


@app.get("/callback")
def callback(request: Request, code: str, state: str):
    stored_state = request.session.get("oauth_state")
    if state != stored_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    token_response = exchange_code_for_token(code)
    user = get_userinfo(token_response["access_token"])
    print("INFO>>>", token_response, user)
    request.session["user"] = user
    request.session["access_token"] = token_response["access_token"]
    request.session["refresh_token"] = token_response["refresh_token"]  # keep it somewhere safe

    return RedirectResponse(url="/")


@app.get("/login")
def login(request: Request):
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    redirect_url = (
        f"{AUTHORIZATION_URL}?response_type=code&scope={SCOPES}"
        f"&client_id={AUTH0_CLIENT_ID}&redirect_uri={quote_plus(APP_URL)}/callback&state={state}"
    )
    return RedirectResponse(url=redirect_url)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        url=f"{LOGOUT_URL}?" + urlencode({"returnTo": APP_URL, "client_id": AUTH0_CLIENT_ID}, quote_via=quote_plus)
    )


@app.get("/")
def home(request: Request):
    user = request.session.get("user")
    if not user:
        return {"message": "Logged out. Login at {APP_URL}/login"}

    return {
        "message": "Logged in. Logout at {APP_URL}/logout",
        "user": request.session.get("user"),
    }
