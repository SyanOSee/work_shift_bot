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

panel_server = {
    'host': os.getenv('PANEL_SERVER_HOST'),
    'port': os.getenv('PANEL_SERVER_PORT'),
    'url': 'http://' + os.getenv('PANEL_SERVER_HOST') + ':' + os.getenv('PANEL_SERVER_PORT'),
    'secret_key': os.getenv('PANEL_SECRET_KEY')
}

database = {
    'host': os.getenv('DATABASE_HOST'),
    'port': os.getenv('DATABASE_PORT'),
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
}

reports = {
    'facility_workers': lambda facility_id: panel_server['url'] + f'/reports/facilities/{facility_id}/users',
    'weekly': panel_server['url'] + '/reports/weekly',
    'monthly': panel_server['url'] + '/reports/monthly',
    'all_users': panel_server['url'] + '/reports/users'
}
