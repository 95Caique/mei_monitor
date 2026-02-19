import logging
from django.conf import settings

try:
    import requests
except Exception:
    requests = None
    import urllib.parse
    import urllib.request

try:
    import telebot
except Exception:
    telebot = None

logger = logging.getLogger(__name__)


_bot_instance = None

def _get_telebot(token):
    global _bot_instance
    if not telebot:
        return None
    if not token:
        return None
    if _bot_instance is None or getattr(_bot_instance, 'token', None) != token:
        try:
            _bot_instance = telebot.TeleBot(token)
        except Exception:
            _bot_instance = None
    return _bot_instance


def send_message(token, chat_id, text):
    """Envia uma mensagem pelo Telegram. Tenta primeiro usar o telebot (pyTelegramBotAPI) e, em caso de falha, recorre ao requests/urllib.
       Retorna True em caso de sucesso e False em caso de falha. Melhorar esse log que ta zuado.
    """
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set; skipping send")
        return False
    if not chat_id:
        logger.warning("No chat_id provided; skipping send")
        return False

    # Prefer telebot if available
    bot = _get_telebot(token)
    if bot:
        try:
            bot.send_message(chat_id, text)
            return True
        except Exception as e:
            logger.exception("Error sending telegram message (telebot): %s", e)
            # fallthrough to requests fallback

    if requests:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        try:
            r = requests.post(url, data=payload, timeout=10)
            r.raise_for_status()
            return True
        except Exception as e:
            logger.exception("Error sending telegram message: %s", e)
            return False
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={urllib.parse.quote_plus(str(chat_id))}&text={urllib.parse.quote_plus(text)}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                return resp.status == 200
        except Exception as e:
            logger.exception("Error sending telegram message (urllib): %s", e)
            return False
