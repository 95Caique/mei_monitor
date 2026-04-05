import logging
from django.conf import settings
import os
from pathlib import Path

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
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


def _load_dotenv_if_needed():
    try:
        if not os.getenv('TELEGRAM_BOT_TOKEN'):
            base = Path(__file__).resolve().parent.parent
            env_path = base / '.env'
            if env_path.exists():
                try:
                    from dotenv import load_dotenv
                    load_dotenv(env_path)
                    logger.debug('Loaded .env from %s', env_path)
                except Exception:
                    logger.debug('python-dotenv não disponível ou falha ao carregar .env')
    except Exception:
        pass


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


def _requests_session_with_retries():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(500, 502, 503, 504))
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session


def send_message(token, chat_id, text):
    """Envia uma mensagem pelo Telegram. Tenta primeiro usar o telebot (pyTelegramBotAPI) e, em caso de falha, recorre ao requests/urllib.
       Retorna True em caso de sucesso e False em caso de falha.
    """
    # se token não foi passado, tenta buscar no settings e, se ainda vazio, tenta recarregar .env
    if not token:
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        _load_dotenv_if_needed()
        token = os.getenv('TELEGRAM_BOT_TOKEN') or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)

    if not token:
        logger.warning('TELEGRAM_BOT_TOKEN not set; skipping send')
        return False
    if not chat_id:
        logger.warning('No chat_id provided; skipping send')
        return False

    bot = _get_telebot(token)
    if bot:
        try:
            bot.send_message(chat_id, text)
            return True
        except Exception as e:
            logger.exception('Error sending telegram message (telebot): %s', e)

    # try requests with retries
    if requests:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {"chat_id": chat_id, "text": text}
        try:
            session = _requests_session_with_retries()
            r = session.post(url, data=payload, timeout=10)
            r.raise_for_status()
            return True
        except Exception as e:
            logger.exception('Error sending telegram message: %s', e)
            return False
    else:
        # fallback para urllib
        try:
            import urllib.parse, urllib.request
            url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={urllib.parse.quote_plus(str(chat_id))}&text={urllib.parse.quote_plus(text)}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                return resp.status == 200
        except Exception as e:
            logger.exception('Error sending telegram message (urllib): %s', e)
            return False
