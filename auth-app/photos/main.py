from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import jwt


SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

app = FastAPI(title="Photos App")


class Client(BaseModel):
    client_id: str
    client_secret: str
    redirect_uris: list[str] = []
    scopes: list[str] = []


db_users = {"test": "test"}
db_photos = {
    "test": [
        "https://upload.wikimedia.org/wikipedia/en/c/cc/Flight_Pattern_Dance.jpeg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Mark_Carney.jpg/1920px-Mark_Carney.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/"
        "Petrosedum_sediforme_445472290.jpg/1280px-Petrosedum_sediforme_445472290.jpg",
    ]
}
db_clients = {
    "printer": Client(
        client_id="printer",
        client_secret="printer_secret",
        redirect_uris=["http://localhost:3000/oauth2-redirect", "http://127.0.0.1:3000/docs/oauth2-redirect"],
        scopes=["photos:read", "user:read"],
    )
}
refresh_tokens = {}
auth_codes = {}


class User(BaseModel):
    username: str
    password: str


class Photo(BaseModel):
    url: str


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    iat = datetime.now(timezone.utc)
    expire = iat + expires_delta
    to_encode.update({"exp": expire, "iat": iat})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/register")
def register(user: User):
    if user.username in db_users:
        raise HTTPException(status_code=400, detail="User already exists")
    db_users[user.username] = user.password
    db_photos[user.username] = []
    return {"message": "User registered successfully"}


@app.get("/authorize")
def authorize(client_id: str, redirect_uri: str, state: str):
    if client_id not in db_clients:
        raise HTTPException(status_code=400, detail="Invalid client ID")
    client = db_clients[client_id]
    print(client_id, redirect_uri, state)
    print("CLIENT", client)
    if redirect_uri not in client.redirect_uris:
        raise HTTPException(status_code=400, detail="Invalid redirect URI")
    auth_code = create_token({"sub": client_id}, timedelta(minutes=5))
    auth_codes[client_id] = auth_code
    redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
    return RedirectResponse(url=redirect_url)


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username not in db_users or db_users[form_data.username] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token({"sub": form_data.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token({"sub": form_data.username}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    refresh_tokens[form_data.username] = refresh_token

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/refresh")
def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token)
    username = payload.get("sub")
    if not username or refresh_tokens.get(username) != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_token({"sub": username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": new_access_token, "token_type": "bearer"}


@app.post("/photos")
def upload_photo(photo: Photo, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    username = payload.get("sub")
    db_photos[username].append(photo.url)
    return {"message": "Photo uploaded"}


@app.get("/photos")
def get_photos(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    username = payload.get("sub")
    return {"photos": db_photos.get(username, [])}
