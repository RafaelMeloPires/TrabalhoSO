"""
Exercício 6.5 — Barbeiro Sonolento
Disciplina: Sistemas Operacionais
Problema: barbearia com 1 barbeiro e N cadeiras de espera.
          Barbeiro dorme quando não há clientes;
          clientes vão embora se todas as cadeiras estão ocupadas.
"""

import threading
import time
import random

CADEIRAS_ESPERA = 3
N_CLIENTES      = 10

# =============================================================================
# VERSÃO SEM PROTEÇÃO (race condition na contagem de clientes)
# =============================================================================

clientes_espera_inseguro = 0

# Simula barbeiro atendendo sem sincronização; contagem de clientes pode ser lida incorretamente.
def barbeiro_inseguro():
    atendidos = 0
    for _ in range(N_CLIENTES):
        time.sleep(random.uniform(0.05, 0.1))
        if clientes_espera_inseguro > 0:
            atendidos += 1
    print(f"[SEM PROTEÇÃO]  Barbeiro atendeu ~{atendidos} clientes (contagem imprecisa)")

# Ocupa ou libera cadeira sem lock; duas threads podem passar pela verificação simultaneamente.
def cliente_inseguro(id_cliente):
    global clientes_espera_inseguro
    if clientes_espera_inseguro < CADEIRAS_ESPERA:
        clientes_espera_inseguro += 1   # race condition aqui!
        time.sleep(random.uniform(0.1, 0.3))
        clientes_espera_inseguro -= 1
    else:
        print(f"  Cliente {id_cliente}: sem cadeira, foi embora (sem proteção)")

# VERSÃO CORRIGIDA (semáforos + mutex)

clientes_sem    = threading.Semaphore(0)
barbeiro_sem    = threading.Semaphore(0)
mutex_barbearia = threading.Lock()

cadeiras_livres = CADEIRAS_ESPERA
estatisticas = {"atendidos": 0, "recusados": 0}

# Dorme em clientes_sem enquanto ocioso; acorda, libera cadeira, chama cliente e realiza o corte.
def barbeiro_seguro():
    while True:
        clientes_sem.acquire()
        with mutex_barbearia:
            global cadeiras_livres
            cadeiras_livres += 1
        barbeiro_sem.release()
        time.sleep(random.uniform(0.03, 0.08))
        with mutex_barbearia:
            estatisticas["atendidos"] += 1
        if estatisticas["atendidos"] + estatisticas["recusados"] >= N_CLIENTES:
            break

# Ocupa cadeira e acorda barbeiro se houver vaga; caso contrário, registra recusa e sai.
def cliente_seguro(id_cliente):
    global cadeiras_livres
    with mutex_barbearia:
        if cadeiras_livres > 0:
            cadeiras_livres -= 1
            clientes_sem.release()
        else:
            estatisticas["recusados"] += 1
            print(f"  Cliente {id_cliente}: sem cadeira, foi embora")
            return
    barbeiro_sem.acquire()

# Executa barbeiro e clientes sem proteção; exibe estimativa imprecisa de atendimentos.
def versao_insegura():
    global clientes_espera_inseguro
    clientes_espera_inseguro = 0
    threads = [threading.Thread(target=barbeiro_inseguro)]
    threads += [threading.Thread(target=cliente_inseguro, args=(i,)) for i in range(N_CLIENTES)]
    for t in threads: t.start()
    for t in threads: t.join()

# Executa barbeiro e clientes com semáforos; exibe contagem exata de atendidos e recusados.
def versao_segura():
    global cadeiras_livres
    cadeiras_livres = CADEIRAS_ESPERA
    estatisticas["atendidos"] = 0
    estatisticas["recusados"] = 0

    b = threading.Thread(target=barbeiro_seguro)
    b.daemon = True
    b.start()

    def lancar_cliente(i):
        time.sleep(random.uniform(0, 0.3))
        cliente_seguro(i)

    threads = [threading.Thread(target=lancar_cliente, args=(i,)) for i in range(N_CLIENTES)]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"[COM SEMÁFOROS] Atendidos={estatisticas['atendidos']} | "
          f"Recusados={estatisticas['recusados']} | "
          f"Total={estatisticas['atendidos'] + estatisticas['recusados']}")

if __name__ == "__main__":
    print("=" * 55)
    print("Exercício 6.5 — Barbeiro Sonolento")
    print("=" * 55)
    versao_insegura()
    versao_segura()
    print()
    print("Justificativa: 'clientes_sem' acorda o barbeiro quando há")
    print("cliente; 'barbeiro_sem' sincroniza a chamada do cliente à")
    print("cadeira de corte. O mutex protege a variável 'cadeiras_livres',")
    print("evitando que dois clientes ocupem a mesma cadeira.")