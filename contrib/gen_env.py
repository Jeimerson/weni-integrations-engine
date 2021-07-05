"""
Responsible for speeding up the generation of a local '.env' configuration file.
OBS: Run in development environment only
"""

import os
from string import ascii_letters, digits, punctuation

from django.utils.crypto import get_random_string


chars = ascii_letters + digits + punctuation

CONFIG_STRING = f"""
DEBUG=True
ALLOWED_HOSTS='*'
SECRET_KEY='{get_random_string(50, chars)}'
DATABASE_URL='postgresql://marketplace:marketplace@localhost:5432/marketplace'
LANGUAGE_CODE='en-us'
TIME_ZONE='America/Maceio'
""".strip()

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

with open(env_path, 'w') as configfile:
    configfile.write(CONFIG_STRING)
