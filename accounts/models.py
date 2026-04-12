from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import os


class User(AbstractUser):
    plano = models.CharField(
        max_length=20,
        choices=(
            ("FREE", "Free"),
            ("PRO", "Pro"),
        ),
        default="FREE",
    )

    lgpd_consentimento = models.BooleanField(
        default=False,
        help_text="Usuário aceitou os termos LGPD",
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text="Foto de perfil do usuário (WebP)",
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Número de telefone/WhatsApp",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.telefone:
            import re
            digits = re.sub(r"\D", "", self.telefone)
            if len(digits) == 11:
                self.telefone = f"({digits[:2]}) {digits[2:7]}-{digits[7:11]}"
            elif len(digits) > 0:
                self.telefone = digits
        
        super().save(*args, **kwargs)
        
        if self.avatar and not self.avatar.name.lower().endswith('.webp'):
            try:
                img = Image.open(self.avatar.path)
                
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        rgb_img.paste(img, mask=img.split()[-1])
                    else:
                        rgb_img.paste(img)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.thumbnail((500, 500), Image.Resampling.LANCZOS)
                
                webp_path = os.path.splitext(self.avatar.path)[0] + '.webp'
                img.save(webp_path, format='WEBP', quality=85, method=6)
                
                if self.avatar.path != webp_path and os.path.isfile(self.avatar.path):
                    os.remove(self.avatar.path)
                
                # Atualizar referência do banco
                base_name = os.path.splitext(self.avatar.name)[0]
                new_name = f'{base_name}.webp'
                self.avatar.name = new_name
                
                User.objects.filter(pk=self.pk).update(avatar=new_name)
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erro ao converter para WebP: {str(e)}")

    def __str__(self):
        return self.username


@receiver(post_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    if instance.avatar and os.path.isfile(instance.avatar.path):
        os.remove(instance.avatar.path)



