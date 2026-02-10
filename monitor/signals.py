from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Invoice, Alert
from telegram_bot.models import TelegramProfile
from telegram_bot.services import send_message
from django.conf import settings


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

    if created:
        msg = f"Nova nota registrada: {instance.invoice_id} - R$ {instance.total} - status {instance.status}"
        Alert.objects.create(empresa=empresa, level='INFO', message=msg)
        try:
            profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
            if profile and token:
                send_message(token, profile.chat_id, msg)
        except Exception:
            pass
    else:
        # detect changes: status or total
        prev_status = getattr(instance, '_prev_status', None)
        prev_total = getattr(instance, '_prev_total', None)
        changes = []
        if prev_status is not None and prev_status != instance.status:
            changes.append(f"status: {prev_status} -> {instance.status}")
        if prev_total is not None and prev_total != instance.total:
            changes.append(f"total: {prev_total} -> {instance.total}")
        if changes:
            msg = f"Nota atualizada: {instance.invoice_id} - {'; '.join(changes)}"
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
    msg = f"Nota removida: {instance.invoice_id} - R$ {instance.total}"
    Alert.objects.create(empresa=empresa, level='WARNING', message=msg)
    try:
        profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
        if profile and token:
            send_message(token, profile.chat_id, msg)
    except Exception:
        pass
