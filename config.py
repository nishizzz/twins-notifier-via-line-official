import os
from dotenv import load_dotenv

# .envファイルの内容を読み込む
load_dotenv()

# TWINS
USER_ID = os.getenv('USER_ID')
PASS = os.getenv('PASS')
NOTIFY_TITLE_LIST = os.getenv('NOTIFY_TITLE_LIST').split(',')

# LINE API
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID').split(',')