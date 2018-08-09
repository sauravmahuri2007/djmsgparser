import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_PATH = os.path.join(BASE_DIR, 'uploads')

MSG_DIR_NAME = 'msg_dir'

MSG_DIR = os.path.join(UPLOAD_PATH, MSG_DIR_NAME)

PARSE_FORMAT = 'json'  # the format in which .msg file will be parsed and saved locally. eg: json, text

JSON_FILE_NAME = 'message.json'

TEXT_FILE_NAME = 'message.text'

