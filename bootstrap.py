import sys
from stravalib.client import Client
from database import Session
from models import StravaCredentials
from config import settings

def bootstrap():
    code = input("Enter the 'code' from the browser URL: ")

    client = Client()
    
    print("Exchanging code for tokens...")
    token_response = client.exchange_code_for_token(
        client_id=settings.STRAVA_CLIENT_ID,
        client_secret=settings.STRAVA_CLIENT_SECRET,
        code=code
    )

    with Session() as session:
        new_creds = StravaCredentials(
            access_token=token_response['access_token'],
            refresh_token=token_response['refresh_token'],
            expires_at=token_response['expires_at']
        )
        session.add(new_creds)
        session.commit()
        print("Successfully bootstrapped Neon DB with Strava tokens!")

if __name__ == "__main__":
    bootstrap()