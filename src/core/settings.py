from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_dialect: str
    db_driver: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    frontend_url: str
    microservice_url: str

    @property
    def db_url(self):
        return f"{self.db_dialect}+{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
