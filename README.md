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
Ela simula um aparelho de ar-condicionado inteligente e será futuramente estruturada.

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