from django.db.models.signals import post_migrate, post_save, post_delete
from django.contrib.auth.models import Group
from django.dispatch import receiver
from estoque.models import Lote # Importe Lote e Produto, se Produto for usado aqui diretamente.



# SINAL para criar grupos
@receiver(post_migrate)
def criar_grupos(sender, **kwargs):
    """
    Cria os grupos 'dono' e 'funcionario' após as migrações serem aplicadas.
    """
    for nome in ['dono', 'funcionario']:
        Group.objects.get_or_create(name=nome)

# SINAIS para atualizar o estoque
@receiver(post_save, sender=Lote)
@receiver(post_delete, sender=Lote)
def atualizar_estoque_produto(sender, instance, **kwargs):
    """
    Recalcula a quantidade em estoque do produto associado
    sempre que um Lote é salvo (criado/atualizado) ou deletado.
    """
    instance.produto.recalcular_quantidade_estoque() # Alterado de 'atualizar_estoque'