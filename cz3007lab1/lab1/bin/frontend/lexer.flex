/* You do not need to change anything up here. */
package lexer;

import frontend.Token;
import static frontend.Token.Type.*;

%%

%public
%final
%class Lexer
%function nextToken
%type Token
%unicode
%line
%column

%{
	/* These two methods are for the convenience of rules to create token objects.
	* If you do not want to use them, delete them
	* otherwise add the code in 
	*/
	
	private Token token(Token.Type type) {
		System.out.format("%s", type);
		String t= yytext();
		//System.out.format("1[%s]", t);
		return new Token(type, yyline, yycolumn, t);
	}
	 
	/* Use this method for rules where you need to process yytext() to get the lexeme of the token.
	 *
	 * Useful for string literals; e.g., the quotes around the literal are part of yytext(),
	 *       but they should not be part of the lexeme. 
	*/
	private Token token(Token.Type type, String text) {
		//System.out.format("2[%s]", text);
		String t= text.substring(1,-1);
		//System.out.format("[%s]", t);
		return new Token(type, yyline, yycolumn, t);
	}
%}

/* This definition may come in handy. If you wish, you can add more definitions here. */
WhiteSpace  = [ ] | \t | \f | \n | \r
Digit		= [0-9]
Alpha		= [a-zA-Z_]

%%
/* put in your rules here.    */

/*Keywords*/
"boolean"	{token(BOOLEAN);}
"break"		{token(BREAK);}
"else"		{token(ELSE);}
"false"		{token(FALSE);}
"if"		{token(IF);}
"import"	{token(IMPORT);}
"int"		{token(INT);}
"module"	{token(MODULE);}
"public"	{token(PUBLIC);}
"return"	{token(RETURN);}
"true"		{token(TRUE);}
"type"		{token(TYPE);}
"void"		{token(VOID);}
"while"		{token(WHILE);}

/*Punctuation Symbols*/
"," {token(COMMA);}
"[" {token(LBRACKET);}
"{" {token(LCURLY);}
"(" {token(LPAREN);}
"]" {token(RBRACKET);}
"}" {token(RCURLY);}
")" {token(RPAREN);}
";" {token(SEMICOLON);}

/*Operators*/
"/" 	{token(DIV);}
"==" 	{token(EQEQ);}
"=" 	{token(EQL);}
">=" 	{token(GEQ);}
">" 	{token(GT);}
"<=" 	{token(LEQ);}
"<" 	{token(LT);}
"-" 	{token(MINUS);}
"!="	{token(NEQ);}
"+" 	{token(PLUS);}
"*" 	{token(TIMES);}

/*Whitespace*/
{WhiteSpace}	{/* ignore */}

/*Identifier*/
{Alpha}({Alpha}|{Digit})* {token(ID);}

/*Literals*/
{Digit}+		{token(INT_LITERAL);}
\"[^\"]*\"		{token(STRING_LITERAL, yytext());}



/* You don't need to change anything below this line. */
.							{ throw new Error("unexpected character '" + yytext() + "'"); }
<<EOF>>						{ return token(EOF); }
