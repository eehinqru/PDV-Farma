from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver

@receiver(post_migrate)
def criar_grupos(sender, **kwargs):
    grupos = ['dono', 'funcionario']
    for nome in grupos:
        Group.objects.get_or_create(name=nome)