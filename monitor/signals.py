from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Invoice, Alert
from telegram_bot.models import TelegramProfile
from telegram_bot.services import send_message
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone


STATUS_PT = {
    'ISSUED': 'Emitida',
    'CANCELLED': 'Cancelada',
    'DRAFT': 'Rascunho',
}

LEVEL_PT = {
    'INFO': 'Informativo',
    'WARNING': 'Atenção',
    'CRITICAL': 'Crítico',
}

MEI_ANNUAL_LIMIT = 81000.00

MEI_ALERT_THRESHOLDS = {
    50000.00: "INFO",     # 50k - informativo
    60000.00: "WARNING",  # 60k - atenção
    70000.00: "WARNING",  # 70k - atenção
    75000.00: "WARNING",  # 75k - atenção crescente
    80000.00: "CRITICAL", # 80k - crítico (muito próximo)
    81000.00: "CRITICAL"  # 81k - limite ultrapassado
}


def format_currency_br(value):
    try:
        v = float(value)
        s = "{:,.2f}".format(v)
        return s.replace(',', 'X').replace('.', ',').replace('X', '.')
    except Exception:
        return str(value)


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
        msg = f"📄 NOVA NOTA CRIADA 📄\nID: {instance.invoice_id}\n💰 Valor: R$ {float(instance.total):.2f}\n📊 Status: {status_label}"
        alert = Alert.objects.create(empresa=empresa, level='INFO', message=msg)
        try:
            profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
            if profile:
                profile_token = profile.bot_token or token
                if profile_token and profile.chat_id:
                    sent = send_message(profile_token, profile.chat_id, msg)
                    if sent:
                        alert.notified = True
                        alert.save(update_fields=['notified'])
        except Exception:
            pass
    else:
        prev_status = getattr(instance, '_prev_status', None)
        prev_total = getattr(instance, '_prev_total', None)
        changes = []

        if prev_status is not None and prev_status != instance.status:
            changes.append(f"Status: de {_status_pt(prev_status)} para {_status_pt(instance.status)}")
        if prev_total is not None and float(prev_total) != float(instance.total):
            changes.append(f"💰 Valor: R$ {float(prev_total):.2f} → R$ {float(instance.total):.2f}")

        if changes:
            msg = f"✏️ NOTA ATUALIZADA ✏️\nNota: {instance.invoice_id}\n\n" + "\n".join(changes)
            alert = Alert.objects.create(empresa=empresa, level='WARNING', message=msg)
            try:
                profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
                if profile:
                    profile_token = profile.bot_token or token
                    if profile_token and profile.chat_id:
                        sent = send_message(profile_token, profile.chat_id, msg)
                        if sent:
                            alert.notified = True
                            alert.save(update_fields=['notified'])
            except Exception:
                pass

    try:
        now = timezone.now()
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        agg = Invoice.objects.filter(empresa=empresa, status='ISSUED', created_at__gte=year_start).aggregate(total=Sum('total'))
        annual_total = float(agg.get('total') or 0)

        level = None
        msg = None

        if annual_total >= 81000.00:
            level = 'CRITICAL'
            msg = f"🚨 LIMITE ULTRAPASSADO 🚨\nSeu faturamento anual ultrapassou o limite de R$ {format_currency_br(MEI_ANNUAL_LIMIT)}.\nTotal atual: R$ {format_currency_br(annual_total)}."
        elif annual_total >= 80000.00:
            level = 'CRITICAL'
            msg = f"🚨 ALERTA CRÍTICO 🚨\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."
        elif annual_total >= 75000.00:
            level = 'WARNING'
            msg = f"⚠️ ATENÇÃO ⚠️\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."
        elif annual_total >= 70000.00:
            level = 'WARNING'
            msg = f"⚠️ ATENÇÃO ⚠️\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."
        elif annual_total >= 60000.00:
            level = 'WARNING'
            msg = f"⚠️ ATENÇÃO ⚠️\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."
        elif annual_total >= 50000.00:
            level = 'INFO'
            msg = f"ℹ️ INFORMATIVO\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."

        if level and msg:
            # Verificar se já foi enviado um alerta similar nas últimas 24h para evitar spam
            since = now - timezone.timedelta(hours=24)
            exists = Alert.objects.filter(empresa=empresa, level=level, message__icontains=f'emitiu R$ {format_currency_br(annual_total)}', created_at__gte=since).exists()
            if not exists:
                alert = Alert.objects.create(empresa=empresa, level=level, message=msg)
                try:
                    profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
                    if profile:
                        profile_token = profile.bot_token or token
                        if profile_token and profile.chat_id:
                            sent = send_message(profile_token, profile.chat_id, msg)
                            if sent:
                                alert.notified = True
                                alert.save(update_fields=['notified'])
                except Exception:
                    pass
    except Exception:
        pass


@receiver(post_delete, sender=Invoice)
def invoice_deleted(sender, instance, **kwargs):
    empresa = instance.empresa
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    msg = f"🗑️ NOTA REMOVIDA 🗑️\nID: {instance.invoice_id}\n💰 Valor: R$ {float(instance.total):.2f}"
    alert = Alert.objects.create(empresa=empresa, level='WARNING', message=msg)
    try:
        profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
        if profile:
            profile_token = profile.bot_token or token
            if profile_token and profile.chat_id:
                sent = send_message(profile_token, profile.chat_id, msg)
                if sent:
                    alert.notified = True
                    alert.save(update_fields=['notified'])
    except Exception:
        pass

    try:
        now = timezone.now()
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        agg = Invoice.objects.filter(empresa=empresa, status='ISSUED', created_at__gte=year_start).aggregate(total=Sum('total'))
        annual_total = float(agg.get('total') or 0)

        # Gerar alertas baseados nos thresholds específicos após remoção
        level = None
        msg2 = None

        # Verificar se ainda está em algum threshold após remoção
        if annual_total >= 81000.00:
            level = 'CRITICAL'
            msg2 = f"🚨 LIMITE ULTRAPASSADO 🚨\nSeu faturamento anual ultrapassou o limite de R$ {format_currency_br(MEI_ANNUAL_LIMIT)}.\nTotal atual: R$ {format_currency_br(annual_total)}."
        elif annual_total >= 80000.00:
            level = 'CRITICAL'
            msg2 = f"🚨 ALERTA CRÍTICO 🚨\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."
        elif annual_total >= 75000.00:
            level = 'WARNING'
            msg2 = f"⚠️ ATENÇÃO ⚠️\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."
        elif annual_total >= 70000.00:
            level = 'WARNING'
            msg2 = f"⚠️ ATENÇÃO ⚠️\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."
        elif annual_total >= 60000.00:
            level = 'WARNING'
            msg2 = f"⚠️ ATENÇÃO ⚠️\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."
        elif annual_total >= 50000.00:
            level = 'INFO'
            msg2 = f"ℹ️ INFORMATIVO\nVocê já emitiu R$ {format_currency_br(annual_total)} em notas.\nLimite: R$ {format_currency_br(MEI_ANNUAL_LIMIT)}."

        if level and msg2:
            # Verificar se já foi enviado um alerta similar nas últimas 24h para evitar spam
            since = now - timezone.timedelta(hours=24)
            exists = Alert.objects.filter(empresa=empresa, level=level, message__icontains=f'emitiu R$ {format_currency_br(annual_total)}', created_at__gte=since).exists()
            if not exists:
                alert2 = Alert.objects.create(empresa=empresa, level=level, message=msg2)
                try:
                    profile = TelegramProfile.objects.filter(user=empresa.user, enabled=True).first()
                    if profile:
                        profile_token = profile.bot_token or token
                        if profile_token and profile.chat_id:
                            sent = send_message(profile_token, profile.chat_id, msg2)
                            if sent:
                                alert2.notified = True
                                alert2.save(update_fields=['notified'])
                except Exception:
                    pass
    except Exception:
        pass
