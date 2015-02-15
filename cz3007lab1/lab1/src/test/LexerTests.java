package test;

import static org.junit.Assert.*;

import java.io.IOException;
import java.io.StringReader;

import lexer.Lexer;

import org.junit.Test;

import frontend.Token;
import frontend.Token.Type;
import static frontend.Token.Type.*;

/**
 * This class contains unit tests for your lexer. You
 * are strongly encouraged to write your own tests.
 */
public class LexerTests {
	// helper method to run tests; no need to change this
	private final void runtest(String input, Token... output) {
		Lexer lexer = new Lexer(new StringReader(input));
		int i=0;
		Token actual, expected;
		try {
			do {
				assertTrue(i < output.length);
				expected = output[i++];
				try {
					actual = lexer.nextToken();
					System.out.format("[%s][%s]", actual, expected);
					assertEquals(expected, actual);
				} catch(Error e) {
					if(expected != null)
						fail(e.getMessage());
					return;
				}
			} while(!actual.isEOF());
		} catch (IOException e) {
			e.printStackTrace();
			fail(e.getMessage());
		}
	}

	/** Example unit test. */
	@Test
	public void testKWs() {
		// first argument to runtest is the string to lex; the remaining arguments
		// are the expected tokens
		runtest("module",//false\nreturn while",
				new Token(MODULE, 0, 0, "module"),
				//new Token(FALSE, 0, 7, "false"),
				//new Token(RETURN, 1, 0, "return"),
				//new Token(WHILE, 1, 7, "while"),
				new Token(EOF, 1, 12, "")
		);
	}

		
	@Test
	public void testStringLiteralWithDoubleQuote() {
		// """
		runtest("\"\"\"",
				(Token)null);
	}
	
	@Test
	public void testStringLiteralEscapeCharacter() {
		// "\n"
		runtest("\"\\n\"",
				new Token(STRING_LITERAL, 0, 0, "\\n"),
				new Token(EOF, 0, 4, ""));
	}
	
}
