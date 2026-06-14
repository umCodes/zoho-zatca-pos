
from app.services.telegram.index import Telegram
from app.core.config import TELEGRAM_BOT_TOKEN


telegram = Telegram(
        bot_token=TELEGRAM_BOT_TOKEN,
        langs = ["am", "ar"]
    )



from app.services.telegram.commands import langs   
from app.services.telegram.commands import photo   
from app.services.telegram.commands import start

from app.services.telegram.states import choose_lang
from app.services.telegram.states import confirm_entry