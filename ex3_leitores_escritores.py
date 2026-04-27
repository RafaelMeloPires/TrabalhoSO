"""
Exercício 6.3 — Leitores e Escritores
Disciplina: Sistemas Operacionais
Problema: múltiplos leitores podem ler simultaneamente; escritores
          necessitam de acesso exclusivo ao recurso compartilhado.
"""

import threading
import time
import random

recurso_compartilhado = {"valor": 0}
log = []

# =============================================================================
# VERSÃO SEM PROTEÇÃO (escritor pode sobrescrever dado em uso)
# =============================================================================

def leitor_inseguro(id_leitor):
    val = recurso_compartilhado["valor"]   # sem garantia de consistência
    time.sleep(random.uniform(0.001, 0.005))
    log.append(f"Leitor-{id_leitor} leu {val}")

def escritor_inseguro(id_escritor, novo_valor):
    # outra thread pode ler valor parcialmente escrito
    recurso_compartilhado["valor"] = novo_valor
    log.append(f"Escritor-{id_escritor} escreveu {novo_valor}")

def versao_insegura():
    log.clear()
    threads = []
    for i in range(4):
        threads.append(threading.Thread(target=leitor_inseguro,   args=(i,)))
    for i in range(2):
        threads.append(threading.Thread(target=escritor_inseguro, args=(i, i * 10)))
    for t in threads: t.start()
    for t in threads: t.join()
    print("[SEM PROTEÇÃO]  Execução concluída (sem garantias de consistência)")
    for entry in log:
        print(f"  {entry}")

# =============================================================================
# VERSÃO CORRIGIDA — preferência a leitores
# Política: leitores têm prioridade; escritor espera não haver leitores.
# =============================================================================

mutex_leitores = threading.Lock()    # protege a contagem de leitores ativos
mutex_escrita  = threading.Lock()    # exclusão mútua para escrita

num_leitores = 0
log_seguro   = []

def leitor_seguro(id_leitor):
    global num_leitores
    # Entrada na seção de leitura
    with mutex_leitores:
        num_leitores += 1
        if num_leitores == 1:          # primeiro leitor bloqueia escritores
            mutex_escrita.acquire()

    # ---- seção de leitura (paralela entre leitores) ----
    val = recurso_compartilhado["valor"]
    time.sleep(random.uniform(0.001, 0.005))
    log_seguro.append(f"Leitor-{id_leitor}  leu {val}")
    # ----------------------------------------------------

    # Saída da seção de leitura
    with mutex_leitores:
        num_leitores -= 1
        if num_leitores == 0:          # último leitor libera escritores
            mutex_escrita.release()

def escritor_seguro(id_escritor, novo_valor):
    with mutex_escrita:                # acesso exclusivo
        recurso_compartilhado["valor"] = novo_valor
        time.sleep(random.uniform(0.002, 0.008))
        log_seguro.append(f"Escritor-{id_escritor} escreveu {novo_valor}")

def versao_segura():
    log_seguro.clear()
    recurso_compartilhado["valor"] = 0
    threads = []
    for i in range(4):
        threads.append(threading.Thread(target=leitor_seguro,   args=(i,)))
    for i in range(2):
        threads.append(threading.Thread(target=escritor_seguro, args=(i, (i + 1) * 10)))
    random.shuffle(threads)
    for t in threads: t.start()
    for t in threads: t.join()
    print("[COM MUTEX]     Execução com exclusão mútua de escritores:")
    for entry in log_seguro:
        print(f"  {entry}")

if __name__ == "__main__":
    print("=" * 55)
    print("Exercício 6.3 — Leitores e Escritores")
    print("=" * 55)
    versao_insegura()
    print()
    versao_segura()
    print()
    print("Justificativa: mutex_escrita garante que escritores tenham")
    print("acesso exclusivo. mutex_leitores protege o contador de")
    print("leitores ativos: o 1º leitor adquire mutex_escrita (bloqueia")
    print("escritores) e o último o libera. Leitores coexistem em paralelo.")
    print("Política adotada: preferência a leitores (escritores aguardam")
    print("até não restar nenhum leitor ativo).")
