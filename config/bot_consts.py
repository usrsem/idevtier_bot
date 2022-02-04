import os
from typing import cast
from loguru import logger as log


API_TOKEN = os.getenv("IDEVTIER_BOT_TOKEN")
if API_TOKEN is None:
    log.error("Add to path your bot token as IDEVTIER_BOT_TOKEN")
    exit()
else:
    cast(str, API_TOKEN)
