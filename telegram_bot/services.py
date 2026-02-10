import logging
from django.conf import settings

try:
    import requests
except Exception:
    requests = None
    import urllib.parse
    import urllib.request

logger = logging.getLogger(__name__)


def send_message(token, chat_id, text):
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set; skipping send")
        return False
    if not chat_id:
        logger.warning("No chat_id provided; skipping send")
        return False

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
