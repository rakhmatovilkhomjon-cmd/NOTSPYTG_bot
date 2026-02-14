import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class BotConfig:
    token: str
    admin_id: int

# Get configuration from environment
def get_config() -> BotConfig:
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("BOT_TOKEN not found in environment variables")
    
    admin_id = os.getenv('ADMIN_ID')
    if not admin_id:
        raise ValueError("ADMIN_ID not found in environment variables")
    
    return BotConfig(
        token=token,
        admin_id=int(admin_id)
    )

config = get_config()