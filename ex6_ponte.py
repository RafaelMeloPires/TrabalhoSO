"""
Exercício 6.6 — Ponte de Mão Única
Disciplina: Sistemas Operacionais
Problema: ponte estreita que só permite tráfego em um sentido por vez.
          Veículos chegam pelos dois lados (Norte e Sul).
          Não pode haver colisão; nenhum sentido deve sofrer inanição.
"""

import threading
import time
import random

N_VEICULOS = 12

# =============================================================================
# VERSÃO SEM PROTEÇÃO (colisão: veículos de sentidos opostos na ponte)
# =============================================================================

na_ponte_inseguro = []

def veiculo_inseguro(id_v, sentido):
    na_ponte_inseguro.append(sentido)
    sentidos_simultaneos = set(na_ponte_inseguro)
    if len(sentidos_simultaneos) > 1:
        print(f"  COLISÃO! Veículo {id_v} ({sentido}) encontrou {sentidos_simultaneos} na ponte!")
    time.sleep(random.uniform(0.01, 0.04))
    na_ponte_inseguro.remove(sentido)

def versao_insegura():
    na_ponte_inseguro.clear()
    threads = []
    for i in range(N_VEICULOS):
        s = "Norte" if i % 2 == 0 else "Sul"
        threads.append(threading.Thread(target=veiculo_inseguro, args=(i, s)))
    for t in threads: t.start()
    for t in threads: t.join()
    print("[SEM PROTEÇÃO]  Travessia sem controle — colisões possíveis")

# =============================================================================
# VERSÃO CORRIGIDA — controle por sentido com prevenção de inanição
# Política: um sentido ocupa a ponte; o outro aguarda.
#           Quando nenhum veículo do sentido atual está na ponte, o outro lado passa.
# =============================================================================

mutex_ponte   = threading.Lock()   # exclusão mútua na atualização dos contadores
ponte_livre   = threading.Lock()   # exclusão mútua para uso da ponte (sentido)

contadores  = {"Norte": 0, "Sul": 0}
log_ordem   = []

# Cada sentido tem seu próprio "primeiro carro abre, último fecha" (Semáforo de leitores)
mutex_norte = threading.Lock()
mutex_sul   = threading.Lock()

def entrar_ponte(sentido):
    mutex = mutex_norte if sentido == "Norte" else mutex_sul
    with mutex:
        contadores[sentido] += 1
        if contadores[sentido] == 1:     # primeiro veículo do sentido trava a ponte
            ponte_livre.acquire()

def sair_ponte(sentido):
    mutex = mutex_norte if sentido == "Norte" else mutex_sul
    with mutex:
        contadores[sentido] -= 1
        if contadores[sentido] == 0:     # último veículo libera a ponte para o outro lado
            ponte_livre.release()

def veiculo_seguro(id_v, sentido):
    entrar_ponte(sentido)
    log_ordem.append(f"Veículo {id_v:02d} ({sentido})")
    print(f"  [{sentido:5s}] Veículo {id_v:02d} na ponte (Norte={contadores['Norte']} Sul={contadores['Sul']})")
    time.sleep(random.uniform(0.02, 0.06))
    sair_ponte(sentido)

def versao_segura():
    contadores["Norte"] = 0
    contadores["Sul"]   = 0
    log_ordem.clear()
    threads = []
    for i in range(N_VEICULOS):
        sentido = "Norte" if i % 2 == 0 else "Sul"
        t = threading.Thread(target=veiculo_seguro, args=(i, sentido))
        threads.append(t)
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"[COM MUTEX]     Ordem de travessia registrada ({len(log_ordem)} veículos):")
    for entry in log_ordem:
        print(f"  {entry}")

if __name__ == "__main__":
    print("=" * 55)
    print("Exercício 6.6 — Ponte de Mão Única")
    print("=" * 55)
    versao_insegura()
    print()
    versao_segura()
    print()
    print("Justificativa: 'ponte_livre' garante exclusividade de sentido.")
    print("O padrão do 1º/último veículo (análogo a leitores-escritores)")
    print("permite que múltiplos veículos do mesmo sentido cruzem em")
    print("paralelo, enquanto o sentido oposto aguarda. Inanição é")
    print("mitigada pelo fato de que assim que o sentido ativo esvazia")
    print("a ponte, o sentido oposto adquire imediatamente o lock.")
