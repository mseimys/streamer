from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import requests

PHOTOS_BASE_URL = "http://localhost:5000"
TOKEN_URL = f"{PHOTOS_BASE_URL}/token"
PHOTOS_LIST_URL = f"{PHOTOS_BASE_URL}/photos"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)

app = FastAPI(title="Printer App")


@app.get("/")
def list_photos(token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(PHOTOS_LIST_URL, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()
