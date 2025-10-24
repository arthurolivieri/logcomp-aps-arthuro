/* A Bison parser, made by GNU Bison 2.3.  */

/* Skeleton interface for Bison's Yacc-like parsers in C

   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006
   Free Software Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor,
   Boston, MA 02110-1301, USA.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* Tokens.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum yytokentype {
     INTEGER = 258,
     IDENTIFIER = 259,
     STRING = 260,
     IF = 261,
     ELSE = 262,
     WHILE = 263,
     REPEAT = 264,
     RULE = 265,
     SET = 266,
     TEMP = 267,
     MODE = 268,
     FAN = 269,
     SWING = 270,
     POWER = 271,
     WAIT = 272,
     SECONDS = 273,
     COOL = 274,
     HEAT = 275,
     DRY = 276,
     AUTO = 277,
     LOW = 278,
     MID = 279,
     HIGH = 280,
     ON = 281,
     OFF = 282,
     HUMIDITY = 283,
     OCCUPIED = 284,
     TIME = 285,
     EQ = 286,
     NE = 287,
     LT = 288,
     LE = 289,
     GT = 290,
     GE = 291,
     UMINUS = 292
   };
#endif
/* Tokens.  */
#define INTEGER 258
#define IDENTIFIER 259
#define STRING 260
#define IF 261
#define ELSE 262
#define WHILE 263
#define REPEAT 264
#define RULE 265
#define SET 266
#define TEMP 267
#define MODE 268
#define FAN 269
#define SWING 270
#define POWER 271
#define WAIT 272
#define SECONDS 273
#define COOL 274
#define HEAT 275
#define DRY 276
#define AUTO 277
#define LOW 278
#define MID 279
#define HIGH 280
#define ON 281
#define OFF 282
#define HUMIDITY 283
#define OCCUPIED 284
#define TIME 285
#define EQ 286
#define NE 287
#define LT 288
#define LE 289
#define GT 290
#define GE 291
#define UMINUS 292




#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef union YYSTYPE
#line 23 "thermolang.y"
{
    int num;
    char *str;
}
/* Line 1529 of yacc.c.  */
#line 128 "thermolang.tab.h"
	YYSTYPE;
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif

extern YYSTYPE yylval;

