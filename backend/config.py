from dotenv import load_dotenv
import os


load_dotenv()


class Settings:
    DB_HOST     : str = os.getenv("DB_HOST", "localhost")
    DB_PORT     : str = os.getenv("DB_PORT", "3306")
    DB_USER     : str = os.getenv("DB_USER", "root")
    DB_PASSWORD : str = os.getenv("DB_PASSWORD", "")
    DB_NAME     : str = os.getenv("DB_NAME", "microvest")
    SECRET_KEY  : str = os.getenv("SECRET_KEY", "2d267b981522e38672ecd10704cb1ad5bd3b50bcff3b649cdde09c808aeb0f96")
    DEBUG       : bool = os.getenv("DEBUG", "False") == "true"


    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()