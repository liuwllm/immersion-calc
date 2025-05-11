import os
from dotenv import load_dotenv

load_dotenv()

JIMAKU_KEY = os.getenv('JIMAKU_KEY')
UPLOAD_FOLDER = "./"