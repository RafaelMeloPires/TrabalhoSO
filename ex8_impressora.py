"""
Exercício 6.8 — Impressora Compartilhada
Disciplina: Sistemas Operacionais
Problema: múltiplos processos disputam o uso de uma única impressora.
          A ordem de chegada deve ser respeitada (FCFS).
          Apenas um processo pode usar a impressora por vez.
"""

import threading
import time
import random
from queue import Queue

N_PROCESSOS = 8

# VERSÃO SEM PROTEÇÃO (impressão simultânea, saída entrelaçada)

saida_insegura = []

# Imprime documento sem exclusão mútua; linhas de processos distintos podem se entrelaçar na saída.
def imprimir_inseguro(id_proc, documento):
    print(f"  Processo {id_proc} iniciou impressão de '{documento}'")
    for linha in range(3):
        time.sleep(random.uniform(0.005, 0.02))
        saida_insegura.append(f"P{id_proc}:linha{linha}")
    print(f"  Processo {id_proc} terminou impressão de '{documento}'")

# Lança todos os processos sem controle; conta e exibe entrelaçamentos detectados no log.
def versao_insegura():
    saida_insegura.clear()
    threads = [
        threading.Thread(target=imprimir_inseguro, args=(i, f"doc_{i}.pdf"))
        for i in range(N_PROCESSOS)
    ]
    for t in threads: t.start()
    for t in threads: t.join()
    processos_vistos = []
    for entrada in saida_insegura:
        p = entrada.split(":")[0]
        if not processos_vistos or processos_vistos[-1] != p:
            processos_vistos.append(p)
    entrelaçamentos = len(processos_vistos) - len(set(processos_vistos))
    print(f"[SEM PROTEÇÃO]  Entrelaçamentos detectados: {entrelaçamentos}")

# VERSÃO CORRIGIDA — fila FCFS + mutex de impressora

fila_impressao   = Queue()
mutex_impressora = threading.Lock()
log_impressao    = []

# Thread dedicada que consome jobs da fila em ordem FCFS com exclusão mútua; encerra ao receber None.
def gerenciador_impressora():
    while True:
        job = fila_impressao.get()
        if job is None:
            break
        id_proc, documento, evento = job
        with mutex_impressora:
            print(f"  [IMPRESSORA] Imprimindo '{documento}' (Processo {id_proc})...")
            log_impressao.append(f"P{id_proc}:{documento}")
            time.sleep(random.uniform(0.03, 0.08))
            print(f"  [IMPRESSORA] Concluído  '{documento}'")
        evento.set()
        fila_impressao.task_done()

# Enfileira o job com um Event e bloqueia até o gerenciador sinalizar a conclusão da impressão.
def processo_seguro(id_proc, documento):
    time.sleep(random.uniform(0, 0.05))
    evento = threading.Event()
    fila_impressao.put((id_proc, documento, evento))
    print(f"  Processo {id_proc} enfileirou '{documento}'")
    evento.wait()
    print(f"  Processo {id_proc} recebeu documento impresso.")

# Inicia o gerenciador, lança todos os processos e encerra a fila ao final; exibe log ordenado.
def versao_segura():
    log_impressao.clear()
    gerenciador = threading.Thread(target=gerenciador_impressora, daemon=True)
    gerenciador.start()

    threads = [
        threading.Thread(target=processo_seguro, args=(i, f"doc_{i}.pdf"))
        for i in range(N_PROCESSOS)
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    fila_impressao.put(None)
    gerenciador.join(timeout=2)

    print(f"[COM FILA FCFS] {len(log_impressao)} documentos impressos em ordem:")
    for i, entry in enumerate(log_impressao, 1):
        print(f"  {i}. {entry}")

if __name__ == "__main__":
    print("=" * 55)
    print("Exercício 6.8 — Impressora Compartilhada")
    print("=" * 55)
    versao_insegura()
    print()
    versao_segura()
    print()
    print("Justificativa: uma thread gerenciadora consome jobs de uma")
    print("Queue (thread-safe por padrão no Python) em ordem FCFS.")
    print("O mutex garante que apenas um job use a impressora por vez.")
    print("Cada processo aguarda seu evento (threading.Event) para")
    print("saber quando seu documento foi impresso.")