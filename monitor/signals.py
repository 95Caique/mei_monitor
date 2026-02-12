from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Invoice, Alert
from telegram_bot.models import TelegramProfile
from telegram_bot.services import send_message
from django.conf import settings


STATUS_PT = {
    'ISSUED': 'Emitida',
    'CANCELLED': 'Cancelada',
    'DRAFT': 'Rascunho',
}

LEVEL_PT = {
    'INFO': 'Info',
    'WARNING': 'Atenção',
    'CRITICAL': 'Crítico',
}


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
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)

    def _status_pt(s):
        return STATUS_PT.get((s or '').upper(), s or '')

    def _level_pt(l):
        return LEVEL_PT.get((l or '').upper(), l or '')

    if created:
        status_label = _status_pt(instance.status)
        msg = f"Nova nota registrada: {instance.invoice_id} — R$ {instance.total:.2f} — {status_label}"
        Alert.objects.create(empresa=empresa, level='INFO', message=msg)
        try:
            profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
            if profile and token:
                send_message(token, profile.chat_id, msg)
        except Exception:
            pass
    else:
        prev_status = getattr(instance, '_prev_status', None)
        prev_total = getattr(instance, '_prev_total', None)
        changes = []
        if prev_status is not None and prev_status != instance.status:
            changes.append(f"status: {_status_pt(prev_status)} -> {_status_pt(instance.status)}")
        if prev_total is not None and float(prev_total) != float(instance.total):
            changes.append(f"valor: R$ {float(prev_total):.2f} -> R$ {float(instance.total):.2f}")
        if changes:
            msg = f"Nota atualizada: {instance.invoice_id} — {'; '.join(changes)}"
            Alert.objects.create(empresa=empresa, level='WARNING', message=msg)
            try:
                profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
                if profile and token:
                    send_message(token, profile.chat_id, msg)
            except Exception:
                pass


@receiver(post_delete, sender=Invoice)
def invoice_deleted(sender, instance, **kwargs):
    empresa = instance.empresa
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    msg = f"Nota removida: {instance.invoice_id} — R$ {instance.total:.2f}"
    Alert.objects.create(empresa=empresa, level='WARNING', message=msg)
    try:
        profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
        if profile and token:
            send_message(token, profile.chat_id, msg)
    except Exception:
        pass
