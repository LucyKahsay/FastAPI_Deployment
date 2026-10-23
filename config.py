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


    database_url: str
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    s3_bucket_name: str
    s3_region: str = "us-east-1"
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    s3_endpoint_url: str | None = None


    max_upload_size_bytes: int = 5* 1024 * 1024


    posts_per_page: int = 10


    reset_token_expire_minutes: int = 60

    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True

    frontend_url: str = "http://localhost:8000"



settings = Settings()  #loaded from .env file  


