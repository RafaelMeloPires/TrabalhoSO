"""
Exercício 6.2 — Produtor-Consumidor com Buffer Limitado
Disciplina: Sistemas Operacionais
Problema: produtor insere itens em buffer circular; consumidor retira.
"""

import threading
import time
import random
from collections import deque

CAPACIDADE = 5
N_ITENS    = 15

# =============================================================================
# VERSÃO SEM PROTEÇÃO (condição de corrida e estouro de buffer)
# =============================================================================

buffer_inseguro = deque()
produzidos_errado  = []
consumidos_errado  = []

def produtor_inseguro(n):
    for i in range(n):
        time.sleep(random.uniform(0.005, 0.02))
        if len(buffer_inseguro) < CAPACIDADE:
            item = f"item-{i}"
            buffer_inseguro.append(item)   # sem lock: outra thread pode ler len() ao mesmo tempo
            produzidos_errado.append(item)

def consumidor_inseguro(n):
    consumidos = 0
    while consumidos < n:
        time.sleep(random.uniform(0.005, 0.02))
        if buffer_inseguro:
            item = buffer_inseguro.popleft()   # sem lock: possível IndexError/dados duplicados
            consumidos_errado.append(item)
            consumidos += 1

def versao_insegura():
    buffer_inseguro.clear()
    t1 = threading.Thread(target=produtor_inseguro,  args=(N_ITENS,))
    t2 = threading.Thread(target=consumidor_inseguro, args=(N_ITENS,))
    t1.start(); t2.start()
    t1.join();  t2.join()
    print(f"[SEM PROTEÇÃO]  Produzidos={len(produzidos_errado)} | Consumidos={len(consumidos_errado)}")
    duplicados = len(consumidos_errado) - len(set(consumidos_errado))
    print(f"                Itens duplicados consumidos: {duplicados}")

# =============================================================================
# VERSÃO CORRIGIDA (semáforos de contagem + mutex)
# =============================================================================

buffer_seguro = deque()
mutex    = threading.Semaphore(1)           # exclusão mútua no buffer
vazios   = threading.Semaphore(CAPACIDADE) # slots disponíveis
cheios   = threading.Semaphore(0)           # itens disponíveis para consumo

produzidos_certo  = []
consumidos_certo  = []

def produtor_seguro(n):
    for i in range(n):
        time.sleep(random.uniform(0.005, 0.02))
        vazios.acquire()       # aguarda slot livre
        mutex.acquire()        # entra na seção crítica
        item = f"item-{i}"
        buffer_seguro.append(item)
        produzidos_certo.append(item)
        mutex.release()        # sai da seção crítica
        cheios.release()       # sinaliza item disponível

def consumidor_seguro(n):
    for _ in range(n):
        time.sleep(random.uniform(0.005, 0.02))
        cheios.acquire()       # aguarda item disponível
        mutex.acquire()
        item = buffer_seguro.popleft()
        consumidos_certo.append(item)
        mutex.release()
        vazios.release()       # libera slot

def versao_segura():
    buffer_seguro.clear()
    t1 = threading.Thread(target=produtor_seguro,  args=(N_ITENS,))
    t2 = threading.Thread(target=consumidor_seguro, args=(N_ITENS,))
    t1.start(); t2.start()
    t1.join();  t2.join()
    print(f"[COM SEMÁFOROS] Produzidos={len(produzidos_certo)} | Consumidos={len(consumidos_certo)}")
    integridade = produzidos_certo == consumidos_certo
    print(f"                Ordem preservada (FIFO): {integridade}")

if __name__ == "__main__":
    print("=" * 55)
    print("Exercício 6.2 — Produtor-Consumidor")
    print("=" * 55)
    versao_insegura()
    versao_segura()
    print()
    print("Justificativa: três semáforos coordenam o acesso:")
    print("  'vazios'  bloqueia o produtor quando buffer está cheio;")
    print("  'cheios'  bloqueia o consumidor quando buffer está vazio;")
    print("  'mutex'   garante exclusão mútua na manipulação do buffer.")
