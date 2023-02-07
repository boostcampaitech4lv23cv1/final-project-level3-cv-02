from db.core.db_login import login
from dotenv import load_dotenv

load_dotenv()

class Settings:
	
    DB_USERNAME : str = login["DB_USERNAME"]
    DB_PASSWORD = login["DB_PASSWORD"]
    DB_HOST : str = login["DB_HOST"]
    DB_PORT : str = login["DB_PORT"]
    DB_DATABASE : str = login["DB_DATABASE"]
	
    DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8"
    
settings = Settings()