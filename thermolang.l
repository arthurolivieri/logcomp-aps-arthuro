%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "thermolang.tab.h"  // Gerado pelo Bison

int line_num = 1;
%}

%option noyywrap

%%

[ \t]+              { /* ignora espaços e tabs */ }
\n                  { line_num++; }
"//".*              { /* ignora comentários de linha */ }

"if"                { return IF; }
"else"              { return ELSE; }
"while"             { return WHILE; }
"repeat"            { return REPEAT; }
"rule"              { return RULE; }
"set"               { return SET; }
"temp"              { return TEMP; }
"mode"              { return MODE; }
"fan"               { return FAN; }
"swing"             { return SWING; }
"power"             { return POWER; }
"wait"              { return WAIT; }
"seconds"           { return SECONDS; }

"cool"              { return COOL; }
"heat"              { return HEAT; }
"dry"               { return DRY; }
"auto"              { return AUTO; }

"low"               { return LOW; }
"mid"               { return MID; }
"high"              { return HIGH; }

"on"                { return ON; }
"off"               { return OFF; }

"humidity"          { return HUMIDITY; }
"occupied"          { return OCCUPIED; }
"time"              { return TIME; }

[a-zA-Z_][a-zA-Z0-9_]*  { 
    yylval.str = strdup(yytext); 
    return IDENTIFIER; 
}

[0-9]+              { 
    yylval.num = atoi(yytext); 
    return INTEGER; 
}

\"[^\"]*\"          { 
    yylval.str = strndup(yytext + 1, strlen(yytext) - 2); 
    return STRING; 
}

"=="                { return EQ; }
"!="                { return NE; }
"<="                { return LE; }
">="                { return GE; }
"<"                 { return LT; }
">"                 { return GT; }

"="                 { return '='; }
"+"                 { return '+'; }
"-"                 { return '-'; }
"*"                 { return '*'; }
"/"                 { return '/'; }
"("                 { return '('; }
")"                 { return ')'; }
"{"                 { return '{'; }
"}"                 { return '}'; }
";"                 { return ';'; }

.                   { 
    printf("Caractere desconhecido: %s (linha %d)\n", yytext, line_num); 
}

%%