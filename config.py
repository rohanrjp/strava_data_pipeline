from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    
    DATABASE_URL:str
    STRAVA_CLIENT_ID:int
    STRAVA_CLIENT_SECRET:str
    
    model_config=SettingsConfigDict(env_file='.env',env_file_encoding='utf-8')
    
settings = Settings()