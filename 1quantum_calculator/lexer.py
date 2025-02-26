from enum import Enum, auto
from typing import List, Optional


class TokenType(Enum):
    NUMBER = auto()
    PLUS = auto()
    MULTIPLY = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


class Token:
    """
    A class to represent a token in the lexer.
    Attributes:
    ----------
    type : str
        The type of the token.
    lexeme : str
        The actual text of the token.
    literal : any, optional
        The literal value of the token, if any (default is None).
    Methods:
    -------
    __str__():
        Returns a string representation of the token.
    """

    def __init__(self, tocke_type, lexeme, literal=None):
        self.type = tocke_type
        self.lexeme = lexeme
        self.literal = literal

    def __str__(self):
        return f"{self.type}: '{self.lexeme}'" + (
            f" ({self.literal})" if self.literal is not None else ""
        )


class Lexer:
    def __init__(self, source: str):
        self.source = source  # The input string to tokenize
        self.current = 0  # Index of the current character being examined
        self.start = 0  # Index of the first character of the current lexeme
        self.tokens = []  # List to store the generated tokens

    def scan_tokens(self) -> List[Token]:
        """
        Scans the source code and generates a list of tokens.

        This method iterates through the source code, identifying and categorizing
        each token until the end of the source is reached. It appends an EOF (End Of File)
        token at the end of the token list.

        Returns:
            List[Token]: A list of tokens identified in the source code.
        """
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None))
        return self.tokens

    # Helper Methods

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    # Processing Individual Tokens

    def scan_token(self) -> None:
        c = self.advance()
        if c == "+":
            self.add_token(TokenType.PLUS)
        elif c == "*":
            self.add_token(TokenType.MULTIPLY)
        elif c == "(":
            self.add_token(TokenType.LPAREN)
        elif c == ")":
            self.add_token(TokenType.RPAREN)
        elif c.isdigit():
            self.number()
        elif c.isspace():
            pass
        else:
            raise ValueError(f"Unexpected character: '{c}'")

    def number(self) -> None:
        """
        Processes a sequence of digits in the source code to form a number token.
        This method consumes all consecutive digit characters from the current
        position in the source code until a non-digit character is encountered
        or the end of the source code is reached. It then converts the sequence
        of digits into an integer value and adds it as a token of type NUMBER.
        Returns:
            None
        """
        while self.peek().isdigit() and not self.is_at_end():
            self.advance()

        value = int(self.source[self.start : self.current])
        self.add_token(TokenType.NUMBER, value)

    def add_token(self, token_type: TokenType, literal: Optional[int] = None) -> None:
        """
        Adds a token to the list of tokens.
        This method creates a new Token object with the given type, lexeme, and literal
        values and appends it to the list of tokens.
        Parameters:
            token_type (TokenType): The type of the token to add.
            literal (any, optional): The literal value of the token, if any (default is None).
        Returns:
            None
        """
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal))
