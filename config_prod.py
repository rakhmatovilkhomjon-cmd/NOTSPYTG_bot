# config_prod.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    token: str
    admin_id: int
    webhook_url: str = None
    webhook_path: str = "/webhook"
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8000

def get_config() -> BotConfig:
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("BOT_TOKEN not found in environment variables")
    
    admin_id = os.getenv('ADMIN_ID')
    if not admin_id:
        raise ValueError("ADMIN_ID not found in environment variables")
        
    webhook_url = os.getenv('WEBHOOK_URL')
    
    return BotConfig(
        token=token,
        admin_id=int(admin_id),
        webhook_url=webhook_url
    )

config = get_config()