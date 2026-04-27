"""
Exercício 6.7 — Estacionamento com Vagas Limitadas
Disciplina: Sistemas Operacionais
Problema: controlar entrada/saída de veículos com capacidade fixa.
          Nenhum veículo pode entrar quando o estacionamento está lotado.
"""

import threading
import time
import random

CAPACIDADE  = 4
N_VEICULOS  = 10

# VERSÃO SEM PROTEÇÃO (permite ocupação acima da capacidade)

vagas_inseguro = CAPACIDADE
log_inseguro   = []

# Verifica e ocupa vaga sem lock; duas threads podem passar pela checagem simultaneamente e causar overflow.
def entrar_inseguro(id_v):
    global vagas_inseguro
    if vagas_inseguro > 0:
        vagas_inseguro -= 1
        log_inseguro.append(f"Veículo {id_v} ENTROU  | vagas livres: {vagas_inseguro}")
        time.sleep(random.uniform(0.05, 0.2))
        vagas_inseguro += 1
        log_inseguro.append(f"Veículo {id_v} SAIU    | vagas livres: {vagas_inseguro}")
    else:
        log_inseguro.append(f"Veículo {id_v} recusado (sem vagas)")

# Lança todos os veículos sem proteção; detecta e exibe overflow no número de vagas.
def versao_insegura():
    global vagas_inseguro
    vagas_inseguro = CAPACIDADE
    log_inseguro.clear()
    threads = [threading.Thread(target=entrar_inseguro, args=(i,)) for i in range(N_VEICULOS)]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"[SEM PROTEÇÃO]  Capacidade={CAPACIDADE}")
    min_vagas = min(
        int(e.split("vagas livres: ")[1]) for e in log_inseguro if "vagas livres" in e
    )
    if min_vagas < 0:
        print(f"  Vagas negativas detectadas: {min_vagas}  → overflow!")
    else:
        print(f"  Mínimo de vagas livres observado: {min_vagas} (pode variar por timing)")


# VERSÃO CORRIGIDA (semáforo de contagem + mutex para o log)


semaforo_vagas = threading.Semaphore(CAPACIDADE)
mutex_log      = threading.Lock()
vagas_atual    = CAPACIDADE
log_seguro     = []

# Bloqueia no semáforo se não há vaga; entra, estaciona e libera a vaga ao sair, atualizando o log com mutex.
def entrar_seguro(id_v):
    global vagas_atual
    semaforo_vagas.acquire()
    with mutex_log:
        vagas_atual -= 1
        log_seguro.append(f"Veículo {id_v:02d} ENTROU  | vagas livres: {vagas_atual}")
        print(f"  Veículo {id_v:02d} ENTROU  | vagas livres: {vagas_atual}")
    time.sleep(random.uniform(0.05, 0.2))
    with mutex_log:
        vagas_atual += 1
        log_seguro.append(f"Veículo {id_v:02d} SAIU    | vagas livres: {vagas_atual}")
        print(f"  Veículo {id_v:02d} SAIU    | vagas livres: {vagas_atual}")
    semaforo_vagas.release()

# Lança todos os veículos com semáforo; verifica invariante de vagas >= 0 e exibe resultado.
def versao_segura():
    global vagas_atual
    vagas_atual = CAPACIDADE
    log_seguro.clear()
    threads = [threading.Thread(target=entrar_seguro, args=(i,)) for i in range(N_VEICULOS)]
    for t in threads: t.start()
    for t in threads: t.join()
    min_vagas = min(
        int(e.split("vagas livres: ")[1]) for e in log_seguro if "vagas livres" in e
    )
    print(f"[COM SEMÁFORO]  Capacidade={CAPACIDADE} | Mínimo de vagas livres: {min_vagas}")
    assert min_vagas >= 0, "Overflow detectado!"
    print("  Invariante respeitada: vagas >= 0 em todos os momentos.")

if __name__ == "__main__":
    print("=" * 55)
    print("Exercício 6.7 — Estacionamento com Vagas Limitadas")
    print("=" * 55)
    versao_insegura()
    print()
    versao_segura()
    print()
    print("Justificativa: o semáforo de contagem inicializado com")
    print(f"CAPACIDADE={CAPACIDADE} bloqueia automaticamente qualquer veículo")
    print("que tente entrar quando todas as vagas estão ocupadas.")
    print("O acquire() decrementa internamente o contador; o release()")
    print("o incrementa. O mutex protege o registro de ocupação atual.")