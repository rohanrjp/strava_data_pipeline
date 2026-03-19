import time
import os
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from stravalib.client import Client

os.environ['SILENCE_TOKEN_WARNINGS'] = 'true'

from database import Session
from models import StravaCredentials, RawStravaActivity

def main():
    with Session() as session:
        stmt = select(StravaCredentials).limit(1)
        stored_creds = session.execute(stmt).scalar_one_or_none()
        
        if not stored_creds: 
            return

        client = Client()

        try:
            token_response = client.refresh_access_token(
                client_id=os.getenv('STRAVA_CLIENT_ID'),
                client_secret=os.getenv('STRAVA_CLIENT_SECRET'),
                refresh_token=stored_creds.refresh_token
            )
            
            client.access_token = token_response['access_token']
            
            stored_creds.access_token = token_response['access_token']
            stored_creds.refresh_token = token_response['refresh_token']
            stored_creds.expires_at = token_response['expires_at']
            session.commit()

        except Exception as e:
            print(f"Auth Error: {e}")
            return

        activities = client.get_activities(limit=5)
        
        for summary in activities:
            print(f"Processing: {summary.name} ({summary.id})")
            
            stream_types = ['time', 'velocity_smooth', 'heartrate', 'distance', 'watts']
            streams_data = {}
            try:
                streams = client.get_activity_streams(summary.id, types=stream_types, resolution='high')
                if streams:
                    for kt, val in streams.items():
                        streams_data[kt] = val.model_dump(mode='json')
            except Exception as e:
                print(f"Stream Error {summary.id}: {e}")

            raw_summary = summary.model_dump(mode='json')

            upsert_stmt = insert(RawStravaActivity).values(
                id=summary.id,
                data=raw_summary,
                streams=streams_data,
                synced_at=func.now()
            ).on_conflict_do_update(
                index_elements=['id'],
                set_={
                    'data': raw_summary,
                    'streams': streams_data,
                    'synced_at': func.now()
                }
            )
            session.execute(upsert_stmt)
            time.sleep(1) 

        session.commit()

if __name__ == "__main__":
    main()