# ThermoLang – Linguagem de Controle para a VM AirConditioner

Criada por: Arthur Olivieri

## Visão Geral
**ThermoLang** é uma linguagem de programação simples e acessível criada para controlar um **ar-condicionado virtual**.  
Ela permite definir regras automáticas de temperatura, umidade e presença, facilitando a criação de rotinas de conforto e economia de energia.

Com ThermoLang você pode:
- Ligar ou desligar o aparelho.
- Definir temperatura alvo.
- Ajustar modo (frio, calor, desumidificação, ventilação).
- Controlar velocidade do ventilador e movimento de aletas.
- Programar ações condicionais baseadas em sensores de **temperatura**, **umidade**, **ocupação** e **horário**.
- Criar laços de repetição e temporizadores.

A sintaxe foi projetada para ser fácil de ler, próxima do português, para que qualquer pessoa com noções básicas de programação consiga usar.

---

## VM AirConditioner
A **AirConditioner VM** é a máquina virtual que executa o código gerado pelo compilador de ThermoLang.  
Ela simula um aparelho de ar-condicionado inteligente com sensores ambientais e controle completo do dispositivo.

**Implementação**: `airconditioner_vm.py`  

### Características da VM
- ✅ **Turing-Completa**: Registradores, memória, comparações e saltos condicionais
- ✅ **10 Registradores**: T0-T9 para computações
- ✅ **4 Sensores**: TEMP, HUMIDITY, OCCUPIED, TIME (read-only)
- ✅ **Modelo Térmico**: Simulação de aquecimento/resfriamento
- ✅ **Controle Completo**: Power, modo, temperatura, ventilador, swing

### Uso da VM

**Executar programa compilado:**
```bash
python3 airconditioner_vm.py output.asm
```

**Executar programas demo:**
```bash
python3 airconditioner_vm.py
```

**Executar testes:**
```bash
python3 test_vm.py
```

---

## Gramática da Linguagem (EBNF)

```
PROGRAM      = { STATEMENT } ;
STATEMENT    = ( ASSIGNMENT
               | IF
               | WHILE
               | REPEAT
               | SETTING
               | WAIT
               | RULE
               | BLOCK
               | ";"
               ), ";"? ;
BLOCK        = "{" { STATEMENT } "}" ;
ASSIGNMENT   = IDENTIFIER "=" EXPR ;
IF           = "if" "(" COND ")" BLOCK [ "else" BLOCK ] ;
WHILE        = "while" "(" COND ")" BLOCK ;
REPEAT       = "repeat" INTEGER BLOCK ;
SETTING      = ( "set" "temp" EXPR
               | "mode" MODE
               | "fan" FANLEVEL
               | "swing" BOOL
               | "power" BOOL
               ) ;
WAIT         = "wait" EXPR "seconds" ;
RULE         = "rule" STRING BLOCK ;
COND         = EXPR ( "==" | "!=" | "<" | "<=" | ">" | ">=" ) EXPR ;
EXPR         = TERM { ( "+" | "-" ) TERM } ;
TERM         = FACTOR { ( "*" | "/" ) FACTOR } ;
FACTOR       = ( ("+"|"-") FACTOR ) | INTEGER | IDENTIFIER
               | SENSOR | "(" EXPR ")" ;
SENSOR       = "temp" | "humidity" | "occupied" | "time" ;
MODE         = "cool" | "heat" | "dry" | "fan" | "auto" ;
FANLEVEL     = "off" | "low" | "mid" | "high" ;
BOOL         = "on" | "off" ;
IDENTIFIER   = LETTER { LETTER | DIGIT | "_" } ;
INTEGER      = DIGIT { DIGIT } ;
STRING       = '"' { LETTER | DIGIT | " " | "_" } '"' ;
LETTER       = "A" | ... | "Z" | "a" | ... | "z" ;
DIGIT        = "0" | "1" | ... | "9" ;
```

---

## Exemplo de Programa ThermoLang

```
rule "eco-night" {
  if (time >= 22*3600 || time < 6*3600) {
    power on;
    mode cool;
    set temp 24;
    fan low;
  } else {
    power on;
    mode cool;
    set temp 22;
    fan mid;
  }
}

rule "presence-boost" {
  if (occupied == 1 && temp > 24) {
    set temp 21;
    fan high;
    wait 600 seconds;
    fan mid;
  }
}
```

# Compilador

## Ferramentas Utilizadas
- **Flex** - Análise Léxica
- **Bison** - Análise Sintática
- **GCC** - Compilação do código C gerado

## Estrutura do Projeto
```
.
├── thermolang.l       # Especificação léxica (Flex)
├── lex.yy.c           # Código C gerado por flex thermolang.l
├── thermolang.y       # Especificação sintática (Bison)
├── thermolang.tab.c   # Código C gerado por thermolang.y
├── thermolang.tab.h   # Arquivo de cabeçalho gerado por thermolang.y
├── test.thermo        # Programa de exemplo
├── thermolang         # Executável gerado por gcc -Wall -g -o thermolang thermolang.tab.c lex.yy.c
├── output.asm         # Assembly gerado por ./thermolang test.thermo output.asm
└── README.md          # Este arquivo
```

## Como Compilar

### Pré-requisitos
```bash
sudo apt-get install flex bison gcc
```

### Compilação do Compilador

**Passo 1: Gerar o parser com Bison**
```bash
bison -d thermolang.y
```

**Passo 2: Gerar o scanner com Flex**
```bash
flex thermolang.l
```

**Passo 3: Compilar tudo**
```bash
gcc -Wall -g -o thermolang thermolang.tab.c lex.yy.c -lfl
```

### Uso
```bash
./thermolang  
```

**Exemplo:**
```bash
./thermolang test.thermo output.asm
cat output.asm
```

## Exemplo de Programa ThermoLang
```thermo
// Controle automático de temperatura
power on;
mode cool;
set temp 22;
fan mid;

if (temp > 25) {
  set temp 23;
  fan high;
}

repeat 3 {
  wait 60 seconds;
}
```

## Assembly Gerado

O compilador gera instruções assembly como:
```assembly
POWER ON
SET_MODE COOL
LOAD_IMM T0, 22
SET_TEMP T0
SET_FAN MID
READ_SENSOR T4, TEMP
LOAD_IMM T5, 25
CMP_GT T6, T4, T5
JZ L0
LOAD_IMM T7, 23
SET_TEMP T7
SET_FAN HIGH
L0:
HALT
```

## Etapas do Compilador

1. **Análise Léxica (Flex)**: Converte código fonte em tokens
2. **Análise Sintática (Bison)**: Valida estrutura gramatical
3. **Geração de Código**: Produz assembly para AirConditioner VM

## Instruções Assembly Suportadas

### Controle do Dispositivo
- `POWER ON/OFF`
- `SET_MODE COOL/HEAT/DRY/FAN/AUTO`
- `SET_TEMP Tn`
- `SET_FAN OFF/LOW/MID/HIGH`
- `SET_SWING ON/OFF`

### Operações
- `LOAD_IMM Tn, valor`
- `ADD/SUB/MUL/DIV Td, T1, T2`
- `CMP_EQ/NE/LT/LE/GT/GE Td, T1, T2`
- `READ_SENSOR Tn, SENSOR`

### Controle de Fluxo
- `JZ/JNZ/JMP Ln`
- `WAIT Tn`
- `HALT`
