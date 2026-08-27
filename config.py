# this config file describes what settings 
# our application needs



from pydantic import SecretStr


# SecretStr means:"This is a string "
# "containing sensitive information, "
# "so don't casually display its actual value."
from pydantic_settings import BaseSettings, SettingsConfigDict  
# "This isn't just an ordinary class."
# " This class represents my application's"
# " settings."And BaseSettings knows how 
# to get configuration values from things 
# like environment variables and .env files.  

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
#  This is basically telling Pydantic Settings:
# "Hey, when you're looking for my configuration "
# "values, also look inside .env."
# "Use the .env file as a source for my settings."
# "Read the .env file using UTF-8 text encoding."
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings()  #loaded from .env file