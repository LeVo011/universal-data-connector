from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Universal Data Connector"
    MAX_RESULTS: int = 10
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()