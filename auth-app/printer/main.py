from os import environ as env

import secrets
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import requests
from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = env.get("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = env.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = env.get("AUTH0_CLIENT_SECRET")
APP_SECRET_KEY = env.get("APP_SECRET_KEY")

APP_CLIENT_ID = "printer"
APP_CLIENT_SECRET = "printer_secret"

MAIN_APP_URL = "http://localhost:5000"
AUTHORIZATION_URL = f"{MAIN_APP_URL}/authorize"
TOKEN_URL = f"{MAIN_APP_URL}/oauth/token"


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=AUTHORIZATION_URL,
    tokenUrl=TOKEN_URL,
)

app = FastAPI(title="Printer App")
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET_KEY, session_cookie="sessionid")


def exchange_code_for_token(code):
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:3000/callback",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
        },
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
    print(token_response)

    return {"message": "OAuth2 Callback Success", "code": code, "state": state}


@app.get("/login")
def login(request: Request):
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    redirect_url = (
        f"{AUTHORIZATION_URL}?response_type=code&client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri=http://localhost:3000/callback&state={state}"
    )
    return RedirectResponse(url=redirect_url)


@app.get("/")
def client_get_photos(token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{MAIN_APP_URL}/photos", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()
