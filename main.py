import time
import os
from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import insert
from stravalib.client import Client

os.environ['SILENCE_TOKEN_WARNINGS'] = 'true'

from database import Session
from models import StravaCredentials, RawStravaActivity
from config import settings

def main():
    with Session() as session:
        stmt = select(StravaCredentials).limit(1)
        stored_creds = session.execute(stmt).scalar_one_or_none()
        if not stored_creds: return

        client = Client(access_token=stored_creds.access_token) 
        
        print("Starting Deep Sync...")
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
                print(f"Could not fetch streams for {summary.id}: {e}")

            zones_data = []
            try:
                zones = client.get_activity_zones(summary.id)
                zones_data = [z.model_dump(mode='json') for z in zones]
            except Exception as e:
                print(f"Could not fetch zones for {summary.id}: {e}")

            raw_summary = summary.model_dump(mode='json')

            upsert_stmt = insert(RawStravaActivity).values(
                id=summary.id,
                data=raw_summary,
                streams=streams_data,
                zones=zones_data,
                synced_at=func.now()
            ).on_conflict_do_update(
                index_elements=['id'],
                set_={
                    'data': raw_summary,
                    'streams': streams_data,
                    'zones': zones_data,
                    'synced_at': func.now()
                }
            )
            session.execute(upsert_stmt)
            
            time.sleep(1) 

        session.commit()
        print("Deep Sync complete! Streams and Zones are now in Neon.")

if __name__ == "__main__":
    main()