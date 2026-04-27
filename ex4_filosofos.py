"""
Exercício 6.4 — Jantar dos Filósofos
Disciplina: Sistemas Operacionais
Problema: 5 filósofos alternam entre pensar e comer.
          Cada filósofo precisa dos 2 garfos adjacentes para comer.
"""

import threading
import time
import random

N = 5   # número de filósofos

# =============================================================================
# VERSÃO COM DEADLOCK (cada filósofo pega o garfo esquerdo antes do direito)
# =============================================================================

garfos_deadlock = [threading.Lock() for _ in range(N)]

def filosofo_deadlock(i, rodadas=3):
    esq = i
    dir = (i + 1) % N
    for _ in range(rodadas):
        # Pensa
        print(f"  Filósofo {i} está pensando...")
        time.sleep(random.uniform(0.01, 0.05))
        # Pega garfo esquerdo
        garfos_deadlock[esq].acquire()
        print(f"  Filósofo {i} pegou garfo {esq} (esquerdo)")
        time.sleep(random.uniform(0.005, 0.02))  # pausa que favorece deadlock
        # Pega garfo direito — PODE DEADLOCKEAR
        garfos_deadlock[dir].acquire()
        print(f"  Filósofo {i} está comendo!")
        time.sleep(random.uniform(0.01, 0.04))
        garfos_deadlock[dir].release()
        garfos_deadlock[esq].release()

def versao_deadlock():
    print("[VERSÃO DEADLOCK] Iniciando — pode travar...")
    threads = [threading.Thread(target=filosofo_deadlock, args=(i,)) for i in range(N)]
    for t in threads: t.start()
    # Aguarda com timeout para não bloquear a demonstração
    for t in threads: t.join(timeout=2.0)
    vivos = [t.is_alive() for t in threads]
    if any(vivos):
        print(f"  DEADLOCK detectado! {sum(vivos)} filósofo(s) ainda bloqueado(s).")
    else:
        print("  Concluído sem deadlock (foi sorte desta vez).")

# =============================================================================
# VERSÃO CORRIGIDA — hierarquia de recursos
# Solução: o filósofo N-1 pega os garfos em ordem INVERSA (dir antes de esq).
# Isso quebra a circularidade e elimina o deadlock.
# =============================================================================

garfos_seguro = [threading.Lock() for _ in range(N)]

def filosofo_seguro(i, rodadas=3):
    if i < N - 1:
        primeiro, segundo = i, (i + 1) % N   # esquerdo → direito
    else:
        primeiro, segundo = (i + 1) % N, i   # INVERTIDO para o último filósofo

    for r in range(rodadas):
        print(f"  Filósofo {i} pensando (rodada {r+1})...")
        time.sleep(random.uniform(0.01, 0.05))
        garfos_seguro[primeiro].acquire()
        garfos_seguro[segundo].acquire()
        print(f"  Filósofo {i} COMENDO (rodada {r+1})!")
        time.sleep(random.uniform(0.01, 0.04))
        garfos_seguro[segundo].release()
        garfos_seguro[primeiro].release()
    print(f"  Filósofo {i} terminou.")

def versao_segura():
    print("[VERSÃO CORRIGIDA] Hierarquia de recursos — sem deadlock:")
    threads = [threading.Thread(target=filosofo_seguro, args=(i,)) for i in range(N)]
    for t in threads: t.start()
    for t in threads: t.join()
    print("  Todos os filósofos terminaram com sucesso!")

if __name__ == "__main__":
    print("=" * 55)
    print("Exercício 6.4 — Jantar dos Filósofos")
    print("=" * 55)
    versao_deadlock()
    print()
    versao_segura()
    print()
    print("Justificativa: o deadlock ocorre quando todos os filósofos")
    print("pegam o garfo esquerdo simultaneamente e aguardam o direito.")
    print("A solução por hierarquia de recursos impõe que um filósofo")
    print("(o N-1) inverta a ordem de aquisição, quebrando o ciclo de")
    print("espera circular que é condição necessária para deadlock.")
