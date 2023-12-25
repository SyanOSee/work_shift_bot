# Standard
import os

# Third-party
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env

BASE = os.path.dirname(os.path.abspath(__file__))

project = {
    'base': BASE,
}

bot = {
    'token': os.getenv('BOT_TOKEN'),
}

media_server = {
    'host': os.getenv('MEDIA_SERVER_HOST'),
    'port': os.getenv('MEDIA_SERVER_PORT')
}

panel_server = {
    'host': os.getenv('PANEL_SERVER_HOST'),
    'port': os.getenv('PANEL_SERVER_PORT'),
    'url': os.getenv('PANEL_SERVER_HOST') + ':' + os.getenv('PANEL_SERVER_PORT'),
    'secret_key': os.getenv('PANEL_SECRET_KEY')
}

database = {
    'host': os.getenv('DATABASE_HOST'),
    'port': os.getenv('DATABASE_PORT'),
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
}
