"""
Exercício 6.1 — Contador Compartilhado
Disciplina: Sistemas Operacionais
Problema: múltiplas threads incrementam/decrementam uma variável compartilhada.

Nota sobre o GIL do Python: o interpretador CPython serializa bytecodes simples,
o que mascara a condição de corrida em operações rápidas. Para tornar a falha
visível, a versão insegura simula explicitamente a não-atomicidade do +=,
separando a leitura, o cálculo e a escrita com uma pausa entre eles — exatamente
o que ocorre a nível de hardware/SO quando o escalonador preempta a thread.
"""

import threading
import time

ITERACOES = 50   # menor número de iterações, pois cada uma tem delay proposital

# =============================================================================
# VERSÃO SEM PROTEÇÃO (demonstra condição de corrida)
# =============================================================================

contador_inseguro = 0

def incrementar_inseguro():
    global contador_inseguro
    for _ in range(ITERACOES):
        # Simula a não-atomicidade: lê → pausa (janela de preempção) → escreve
        temp = contador_inseguro   # 1. leitura
        time.sleep(0.0001)         # 2. outra thread pode alterar o valor aqui!
        contador_inseguro = temp + 1  # 3. escrita com valor desatualizado

def decrementar_inseguro():
    global contador_inseguro
    for _ in range(ITERACOES):
        temp = contador_inseguro
        time.sleep(0.0001)
        contador_inseguro = temp - 1

def versao_insegura():
    global contador_inseguro
    contador_inseguro = 0
    t1 = threading.Thread(target=incrementar_inseguro)
    t2 = threading.Thread(target=decrementar_inseguro)
    t1.start(); t2.start()
    t1.join();  t2.join()
    print(f"[SEM PROTEÇÃO]  Resultado esperado: 0 | Resultado obtido: {contador_inseguro}")

# =============================================================================
# VERSÃO CORRIGIDA (exclusão mútua com Lock)
# =============================================================================

contador_seguro = 0
lock = threading.Lock()

def incrementar_seguro():
    global contador_seguro
    for _ in range(ITERACOES):
        with lock:                     # <-- seção crítica protegida
            temp = contador_seguro
            time.sleep(0.0001)         # mesmo delay — mas agora protegido
            contador_seguro = temp + 1

def decrementar_seguro():
    global contador_seguro
    for _ in range(ITERACOES):
        with lock:
            temp = contador_seguro
            time.sleep(0.0001)
            contador_seguro = temp - 1

def versao_segura():
    global contador_seguro
    contador_seguro = 0
    t1 = threading.Thread(target=incrementar_seguro)
    t2 = threading.Thread(target=decrementar_seguro)
    t1.start(); t2.start()
    t1.join();  t2.join()
    print(f"[COM LOCK]      Resultado esperado: 0 | Resultado obtido: {contador_seguro}")

if __name__ == "__main__":
    print("=" * 55)
    print("Exercício 6.1 — Contador Compartilhado")
    print("=" * 55)
    versao_insegura()
    versao_segura()
    print()
    print("Justificativa: sem o Lock, o += não é atômico no CPython")
    print("(envolve LOAD, ADD e STORE), permitindo que duas threads")
    print("leiam o mesmo valor antes que qualquer uma o atualize,")
    print("causando perda de escritas. O Lock garante exclusão mútua.")
