# Relatório Técnico — Sincronização de Processos

**Disciplina:** Sistemas Operacionais  
**Atividade:** Prática de Programação — Sincronização  
**Linguagem:** Python 3 (`threading`, `queue`)

---

## 1. Metodologia Geral

Cada exercício foi implementado em duas versões:

| Versão | Objetivo |
|--------|----------|
| **Insegura** | Evidenciar a falha de concorrência (race condition, deadlock, overflow) |
| **Corrigida** | Aplicar o mecanismo de sincronização adequado |

---

## 2. Exercícios

### 6.1 — Contador Compartilhado (`ex1_contador.py`)

**Falha:** o operador `+=` não é atômico — envolve três instruções (LOAD, ADD, STORE). Duas threads podem ler o mesmo valor antes de qualquer escrita, causando perda de incrementos.

**Correção:** `threading.Lock` protege a seção crítica, garantindo que apenas uma thread por vez execute a leitura-modificação-escrita.

**Mecanismo:** Mutex (`Lock`)

---

### 6.2 — Produtor-Consumidor (`ex2_produtor_consumidor.py`)

**Falha:** sem sincronização, produtor pode inserir além da capacidade e consumidor pode consumir itens duplicados ou inexistentes.

**Correção:** três semáforos cooperam:
- `vazios` (iniciado em CAPACIDADE): bloqueia o produtor quando o buffer está cheio;
- `cheios` (iniciado em 0): bloqueia o consumidor quando o buffer está vazio;
- `mutex`: exclusão mútua na manipulação do buffer circular.

**Mecanismo:** Semáforos de contagem + Mutex

---

### 6.3 — Leitores e Escritores (`ex3_leitores_escritores.py`)

**Falha:** sem controle, escritores podem sobrescrever dados enquanto leitores os acessam.

**Correção:** política de **preferência a leitores**:
- O 1º leitor adquire `mutex_escrita`, bloqueando escritores;
- Leitores subsequentes coexistem em paralelo;
- O último leitor libera `mutex_escrita`.
- `mutex_leitores` protege o contador de leitores ativos.

**Mecanismo:** dois Mutexes (padrão readers-writers clássico)

---

### 6.4 — Jantar dos Filósofos (`ex4_filosofos.py`)

**Falha:** todos os filósofos pegam o garfo esquerdo simultaneamente e aguardam o direito indefinidamente → **deadlock circular** (espera circular entre todos os N processos).

**Correção:** **hierarquia de recursos** — o filósofo N−1 inverte a ordem de aquisição (pega o direito antes do esquerdo). Isso quebra a espera circular, eliminando o deadlock sem risco de inanição.

**Mecanismo:** Locks ordenados por hierarquia de índice

---

### 6.5 — Barbeiro Sonolento (`ex5_barbeiro.py`)

**Falha:** sem proteção, múltiplos clientes podem decrementar o contador de cadeiras ao mesmo tempo, corrompendo a contagem.

**Correção:**
- `clientes_sem`: acorda o barbeiro quando há cliente;
- `barbeiro_sem`: cliente aguarda ser chamado à cadeira de corte;
- `mutex`: protege o acesso à variável `cadeiras_livres`.

**Mecanismo:** dois Semáforos + Mutex

---

### 6.6 — Ponte de Mão Única (`ex6_ponte.py`)

**Falha:** veículos de sentidos opostos entram na ponte simultaneamente, simulando colisão.

**Correção:** padrão análogo a leitores-escritores por sentido:
- `ponte_livre` garante que apenas um sentido use a ponte;
- O 1º veículo de um sentido adquire `ponte_livre`; o último a libera;
- Mutexes separados por sentido protegem os contadores.

**Política de inanição:** ao esvaziar, o sentido ativo libera imediatamente o lock para o oposto.

**Mecanismo:** Locks + padrão 1º/último veículo

---

### 6.7 — Estacionamento (`ex7_estacionamento.py`)

**Falha:** dois veículos podem ler `vagas > 0` antes de qualquer decremento e ambos entrarem, excedendo a capacidade.

**Correção:** semáforo de contagem inicializado com `CAPACIDADE`:
- `acquire()` bloqueia quando não há vaga;
- `release()` é chamado na saída, liberando a vaga;
- Mutex protege o registro de ocupação para o log.

**Invariante verificada:** `vagas >= 0` em todos os instantes.

**Mecanismo:** Semáforo de contagem + Mutex

---

### 6.8 — Impressora Compartilhada (`ex8_impressora.py`)

**Falha:** múltiplos processos acessam a impressora simultaneamente, causando saída entrelaçada e incoerente.

**Correção:**
- `Queue` (thread-safe) armazena jobs em ordem FCFS;
- Thread gerenciadora processa os jobs sequencialmente;
- `mutex_impressora` garante exclusão mútua na impressão;
- `threading.Event` notifica cada processo quando seu documento foi impresso.

**Mecanismo:** Fila FCFS + Mutex + Event

---

## 3. Resumo dos Mecanismos Utilizados

| Exercício | Mecanismo Principal | Padrão |
|-----------|---------------------|--------|
| 6.1 Contador | Lock | Exclusão mútua simples |
| 6.2 Prod-Cons | Semáforos + Mutex | Buffer limitado clássico |
| 6.3 Leit-Escrit | Dois Mutexes | Readers-Writers (pref. leitores) |
| 6.4 Filósofos | Locks hierárquicos | Hierarquia de recursos |
| 6.5 Barbeiro | Semáforos + Mutex | Rendezvous |
| 6.6 Ponte | Locks + contador | Readers-Writers adaptado |
| 6.7 Estaciona | Semáforo contagem | Contador de recursos |
| 6.8 Impressora | Queue + Mutex + Event | Fila de jobs FCFS |

---

## 4. Conclusão

Os problemas clássicos de sincronização ilustram os três principais desafios de ambientes concorrentes:

1. **Race condition** — acesso não-atômico a dados compartilhados (exercícios 6.1, 6.2, 6.7, 6.8);
2. **Deadlock** — espera circular entre processos (exercício 6.4);
3. **Inanição** — um processo nunca obtém o recurso (tratado em 6.3 e 6.6).

A escolha correta do mecanismo de sincronização — semáforo, mutex, variável de condição ou fila — depende da natureza do problema: se há controle de quantidade (semáforo), exclusão simples (mutex), ordem garantida (fila), ou espera por evento (Event/Condition).
