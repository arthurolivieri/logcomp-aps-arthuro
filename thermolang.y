%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex();
extern int yyparse();
extern FILE *yyin;
extern int line_num;

void yyerror(const char *s);

FILE *output_file;
int label_count = 0;
int temp_count = 0;

// Funções auxiliares
int new_label() { return label_count++; }
int new_temp() { return temp_count++; }

%}

%union {
    int num;
    char *str;
}

%token <num> INTEGER
%token <str> IDENTIFIER STRING
%token IF ELSE WHILE REPEAT RULE SET TEMP MODE FAN SWING POWER WAIT SECONDS
%token COOL HEAT DRY AUTO LOW MID HIGH ON OFF
%token HUMIDITY OCCUPIED TIME
%token EQ NE LT LE GT GE

%left '+' '-'
%left '*' '/'
%right UMINUS

%type <num> expr term factor

%%

program:
    /* vazio */
    | program statement
    ;

statement:
    assignment ';'
    | if_stmt
    | while_stmt
    | repeat_stmt
    | setting ';'
    | wait_stmt ';'
    | rule_stmt
    | block
    | ';'
    ;

block:
    '{' statement_list '}'
    ;

statement_list:
    /* vazio */
    | statement_list statement
    ;

assignment:
    IDENTIFIER '=' expr {
        fprintf(output_file, "STORE %s, T%d\n", $1, $3);
        free($1);
    }
    ;

if_stmt:
    IF '(' condition ')' {
        int label = new_label();
        fprintf(output_file, "JZ L%d\n", label);
        fprintf(output_file, "; IF body\n");
    } block {
        fprintf(output_file, "L%d:\n", label_count - 1);
    }
    | IF '(' condition ')' {
        int label_else = new_label();
        int label_end = new_label();
        fprintf(output_file, "JZ L%d\n", label_else);
    } block ELSE {
        fprintf(output_file, "JMP L%d\n", label_count - 1);
        fprintf(output_file, "L%d:\n", label_count - 2);
    } block {
        fprintf(output_file, "L%d:\n", label_count - 1);
    }
    ;

while_stmt:
    WHILE '(' {
        int label_start = new_label();
        fprintf(output_file, "L%d:\n", label_start);
    } condition ')' {
        int label_end = new_label();
        fprintf(output_file, "JZ L%d\n", label_end);
    } block {
        fprintf(output_file, "JMP L%d\n", label_count - 2);
        fprintf(output_file, "L%d:\n", label_count - 1);
    }
    ;

repeat_stmt:
    REPEAT INTEGER {
        int label_start = new_label();
        int counter = new_temp();
        fprintf(output_file, "LOAD_IMM T%d, %d\n", counter, $2);
        fprintf(output_file, "L%d:\n", label_start);
    } block {
        int label_start = label_count - 1;
        fprintf(output_file, "DEC T%d\n", temp_count - 1);
        fprintf(output_file, "JNZ L%d\n", label_start);
    }
    ;

setting:
    SET TEMP expr {
        fprintf(output_file, "SET_TEMP T%d\n", $3);
    }
    | MODE COOL {
        fprintf(output_file, "SET_MODE COOL\n");
    }
    | MODE HEAT {
        fprintf(output_file, "SET_MODE HEAT\n");
    }
    | MODE DRY {
        fprintf(output_file, "SET_MODE DRY\n");
    }
    | MODE AUTO {
        fprintf(output_file, "SET_MODE AUTO\n");
    }
    | FAN LOW {
        fprintf(output_file, "SET_FAN LOW\n");
    }
    | FAN MID {
        fprintf(output_file, "SET_FAN MID\n");
    }
    | FAN HIGH {
        fprintf(output_file, "SET_FAN HIGH\n");
    }
    | FAN OFF {
        fprintf(output_file, "SET_FAN OFF\n");
    }
    | SWING ON {
        fprintf(output_file, "SET_SWING ON\n");
    }
    | SWING OFF {
        fprintf(output_file, "SET_SWING OFF\n");
    }
    | POWER ON {
        fprintf(output_file, "POWER ON\n");
    }
    | POWER OFF {
        fprintf(output_file, "POWER OFF\n");
    }
    ;

wait_stmt:
    WAIT expr SECONDS {
        fprintf(output_file, "WAIT T%d\n", $2);
    }
    ;

rule_stmt:
    RULE STRING {
        fprintf(output_file, "; RULE: %s\n", $2);
        free($2);
    } block
    ;

condition:
    expr EQ expr {
        int temp = new_temp();
        fprintf(output_file, "CMP_EQ T%d, T%d, T%d\n", temp, $1, $3);
    }
    | expr NE expr {
        int temp = new_temp();
        fprintf(output_file, "CMP_NE T%d, T%d, T%d\n", temp, $1, $3);
    }
    | expr LT expr {
        int temp = new_temp();
        fprintf(output_file, "CMP_LT T%d, T%d, T%d\n", temp, $1, $3);
    }
    | expr LE expr {
        int temp = new_temp();
        fprintf(output_file, "CMP_LE T%d, T%d, T%d\n", temp, $1, $3);
    }
    | expr GT expr {
        int temp = new_temp();
        fprintf(output_file, "CMP_GT T%d, T%d, T%d\n", temp, $1, $3);
    }
    | expr GE expr {
        int temp = new_temp();
        fprintf(output_file, "CMP_GE T%d, T%d, T%d\n", temp, $1, $3);
    }
    ;

expr:
    term { $$ = $1; }
    | expr '+' term {
        int temp = new_temp();
        fprintf(output_file, "ADD T%d, T%d, T%d\n", temp, $1, $3);
        $$ = temp;
    }
    | expr '-' term {
        int temp = new_temp();
        fprintf(output_file, "SUB T%d, T%d, T%d\n", temp, $1, $3);
        $$ = temp;
    }
    ;

term:
    factor { $$ = $1; }
    | term '*' factor {
        int temp = new_temp();
        fprintf(output_file, "MUL T%d, T%d, T%d\n", temp, $1, $3);
        $$ = temp;
    }
    | term '/' factor {
        int temp = new_temp();
        fprintf(output_file, "DIV T%d, T%d, T%d\n", temp, $1, $3);
        $$ = temp;
    }
    ;

factor:
    INTEGER {
        int temp = new_temp();
        fprintf(output_file, "LOAD_IMM T%d, %d\n", temp, $1);
        $$ = temp;
    }
    | IDENTIFIER {
        int temp = new_temp();
        fprintf(output_file, "LOAD T%d, %s\n", temp, $1);
        free($1);
        $$ = temp;
    }
    | TEMP {
        int temp = new_temp();
        fprintf(output_file, "READ_SENSOR T%d, TEMP\n", temp);
        $$ = temp;
    }
    | HUMIDITY {
        int temp = new_temp();
        fprintf(output_file, "READ_SENSOR T%d, HUMIDITY\n", temp);
        $$ = temp;
    }
    | OCCUPIED {
        int temp = new_temp();
        fprintf(output_file, "READ_SENSOR T%d, OCCUPIED\n", temp);
        $$ = temp;
    }
    | TIME {
        int temp = new_temp();
        fprintf(output_file, "READ_SENSOR T%d, TIME\n", temp);
        $$ = temp;
    }
    | '(' expr ')' { $$ = $2; }
    | '-' factor %prec UMINUS {
        int temp = new_temp();
        fprintf(output_file, "NEG T%d, T%d\n", temp, $2);
        $$ = temp;
    }
    | '+' factor %prec UMINUS { $$ = $2; }
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Erro na linha %d: %s\n", line_num, s);
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Uso: %s <input.thermo> <output.asm>\n", argv[0]);
        return 1;
    }

    yyin = fopen(argv[1], "r");
    if (!yyin) {
        perror("Erro ao abrir arquivo de entrada");
        return 1;
    }

    output_file = fopen(argv[2], "w");
    if (!output_file) {
        perror("Erro ao criar arquivo de saída");
        return 1;
    }

    fprintf(output_file, "; ThermoLang Assembly Output\n");
    fprintf(output_file, "; Generated from: %s\n\n", argv[1]);

    yyparse();

    fprintf(output_file, "\nHALT\n");

    fclose(yyin);
    fclose(output_file);

    printf("Compilação concluída! Assembly gerado em: %s\n", argv[2]);
    return 0;
}