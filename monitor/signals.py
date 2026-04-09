from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Invoice, Alert
from telegram_bot.models import TelegramProfile
from telegram_bot.services import send_message
from django.conf import settings
from django.db.models import Sum, Q
from django.utils import timezone
from django.db import transaction
import logging
import threading

logger = logging.getLogger(__name__)

STATUS_PT = {
    'ISSUED': 'Emitida',
    'CANCELLED': 'Cancelada',
    'DRAFT': 'Rascunho',
}

def format_currency_br(value):
    try:
        v = float(value)
        s = "{:,.2f}".format(v)
        return s.replace(',', 'X').replace('.', ',').replace('X', '.')
    except Exception:
        return str(value)


def _send_telegram_async(alert_id):
    try:
        alert = Alert.objects.get(id=alert_id)
        profile = TelegramProfile.objects.filter(user=alert.empresa.user, enabled=True).first()
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        
        if profile and (profile.bot_token or token) and profile.chat_id:
            profile_token = profile.bot_token or token
            sent = send_message(profile_token, profile.chat_id, alert.message)
            if sent:
                alert.notified = True
                alert.save(update_fields=['notified'])
    except Exception as e:
        logger.error(f"Erro ao enviar Telegram para alerta {alert_id}: {e}")


@receiver(pre_save, sender=Invoice)
def invoice_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = Invoice.objects.get(pk=instance.pk)
            instance._prev_status = prev.status
            instance._prev_total = prev.total
        except Invoice.DoesNotExist:
            instance._prev_status = None
            instance._prev_total = None
    else:
        instance._prev_status = None
        instance._prev_total = None


@receiver(post_save, sender=Invoice)
def invoice_saved(sender, instance, created, **kwargs):
    empresa = instance.empresa

    if created:
        status_label = STATUS_PT.get((instance.status or '').upper(), instance.status or '')
        msg = f"📄 NOVA NOTA CRIADA 📄\nID: {instance.invoice_id}\n💰 Valor: R$ {float(instance.total):.2f}\n📊 Status: {status_label}"
        
        alert = Alert.objects.create(empresa=empresa, level='INFO', message=msg, notified=False)
        
        thread = threading.Thread(target=_send_telegram_async, args=(alert.id,), daemon=True)
        thread.start()
        
    else:
        prev_status = getattr(instance, '_prev_status', None)
        prev_total = getattr(instance, '_prev_total', None)
        changes = []

        if prev_status is not None and prev_status != instance.status:
            changes.append(f"Status: de {STATUS_PT.get(prev_status, prev_status)} para {STATUS_PT.get(instance.status, instance.status)}")
        if prev_total is not None and float(prev_total) != float(instance.total):
            changes.append(f"💰 Valor: R$ {float(prev_total):.2f} → R$ {float(instance.total):.2f}")

        if changes:
            msg = f"✏️ NOTA ATUALIZADA ✏️\nNota: {instance.invoice_id}\n\n" + "\n".join(changes)
            alert = Alert.objects.create(empresa=empresa, level='WARNING', message=msg, notified=False)
            
            thread = threading.Thread(target=_send_telegram_async, args=(alert.id,), daemon=True)
            thread.start()

    _process_annual_limit_alerts(empresa, instance)


@receiver(post_delete, sender=Invoice)
def invoice_deleted(sender, instance, **kwargs):
    """Otimizado: Telegram via thread assíncrona"""
    empresa = instance.empresa
    msg = f"🗑️ NOTA REMOVIDA 🗑️\nID: {instance.invoice_id}\n💰 Valor: R$ {float(instance.total):.2f}"
    alert = Alert.objects.create(empresa=empresa, level='WARNING', message=msg, notified=False)
    
    thread = threading.Thread(target=_send_telegram_async, args=(alert.id,), daemon=True)
    thread.start()
    
    _process_annual_limit_alerts(empresa, instance, is_delete=True)


def _process_annual_limit_alerts(empresa, instance, is_delete=False):
    try:
        now = timezone.now()
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        agg = Invoice.objects.filter(
            empresa=empresa, 
            status='ISSUED', 
            created_at__gte=year_start
        ).aggregate(total=Sum('total'))
        
        annual_total = float(agg.get('total') or 0)
        level = None
        msg = None

        # Determinar nível único
        if annual_total >= 81000.00:
            level, msg = 'CRITICAL', f"🚨 LIMITE ULTRAPASSADO 🚨\nSeu faturamento: R$ {format_currency_br(annual_total)}\nLimite: R$ {format_currency_br(81000.00)}"
        elif annual_total >= 80000.00:
            level, msg = 'CRITICAL', f"🚨 CRÍTICO ⚠️\nSeu faturamento: R$ {format_currency_br(annual_total)}\nLimite: R$ {format_currency_br(81000.00)}"
        elif annual_total >= 75000.00:
            level, msg = 'WARNING', f"⚠️ ATENÇÃO\nSeu faturamento: R$ {format_currency_br(annual_total)}\nLimite: R$ {format_currency_br(81000.00)}"
        elif annual_total >= 60000.00:
            level, msg = 'WARNING', f"⚠️ ATENÇÃO\nSeu faturamento: R$ {format_currency_br(annual_total)}\nLimite: R$ {format_currency_br(81000.00)}"
        elif annual_total >= 50000.00:
            level, msg = 'INFO', f"ℹ️ INFO\nSeu faturamento: R$ {format_currency_br(annual_total)}\nLimite: R$ {format_currency_br(81000.00)}"

        if level and msg:
            since = now - timezone.timedelta(hours=24)
            exists = Alert.objects.filter(
                empresa=empresa, 
                level=level, 
                created_at__gte=since
            ).exists()
            
            if not exists:
                alert = Alert.objects.create(empresa=empresa, level=level, message=msg, notified=False)
                
                thread = threading.Thread(target=_send_telegram_async, args=(alert.id,), daemon=True)
                thread.start()
                
    except Exception as e:
        logger.exception(f"Erro ao processar alertas de limite: {e}")
