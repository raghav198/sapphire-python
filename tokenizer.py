# coding=utf-8
from enum import Enum, auto
import re


class TokenError(Exception):
    pass

class TokenType(Enum):
        STR = auto()
        NUM = auto()
        ASSIGN = auto()
        ADD = auto()
        SUB = auto()
        MUL = auto()
        DIV = auto()
        LPAR = auto()
        RPAR = auto()
        LBLK = auto()
        RBLK = auto()
        THEN = auto()
        ELSE = auto()
        EXP = auto()
        ID = auto()
        TERM = auto()
        GT = auto()
        LT = auto()
        EQ = auto()
        GE = auto()
        LE = auto()
        EOF = auto()
        AND = auto()
        OR = auto()
        NOT = auto()
        XOR = auto()
        EOL = auto()
        LARG = auto()
        RARG = auto()
        SEPARG = auto()


class Token:
    def __init__(self, tok: TokenType, val=None):
        self.type = tok
        self.value = val
        self.tokenList = []

    def __str__(self):
        return f'{self.type.name}{("(" + str(self.value) + ")") if self.value is not None else ""}'
    __repr__ = __str__


class Tokenizer:
    def __init__(self, stream: str, patterns: dict=None):
        self.stream = stream
        self.patterns = patterns

    def tokens(self, debug=False):
        def match(tok, string, capture=False):
            # input(f'matching {string}')
            if self.stream.startswith(string):
                # print(f'matched [{string}]')
                self.stream = self.stream[len(string):]
                # print(f'<<{self.stream}>> remains')
                return Token(tok, string) if capture else Token(tok)
            return False

        self.stream = self.stream.lstrip()
        while len(self.stream):
            self.stream = self.stream.lstrip()
            if debug:
                input()
                print('###' + self.stream)
            if self.stream[0].isdigit():
                number, rest = re.match(r'(\d+)(.*)', self.stream, re.MULTILINE).groups()
                # print(f'found number {number}; {{{rest}}} remains!')
                self.stream = self.stream[len(number):]
                yield Token(TokenType.NUM, int(number))
            elif self.stream[0] in "'\"":
                string, rest = re.match(rf'{self.stream[0]}(.*?){self.stream[0]}(.*)', self.stream, re.MULTILINE).groups()
                # print(f'found string {string}; {{{rest}}} remains!')
                self.stream = self.stream[len(string) + 2:]
                yield Token(TokenType.STR, string)
            elif self.stream[0].isalpha():
                ident, rest = re.match(r'([a-z]+)(.*)', self.stream, re.MULTILINE).groups()
                # print(f'found ID {ident}; {{{rest}}} remains!')
                self.stream = self.stream[len(ident):]
                yield Token(TokenType.ID, ident)
            else:
                yield match(TokenType.ASSIGN, ':-') or \
                      match(TokenType.LBLK, '{{') or \
                      match(TokenType.RBLK, '}}') or \
                      match(TokenType.THEN, '=>') or \
                      match(TokenType.ELSE, '!!') or \
                      match(TokenType.OR, '||') or \
                      match(TokenType.AND, '&&') or \
                      match(TokenType.GE, '>=') or \
                      match(TokenType.GE, '<=') or \
                      match(TokenType.LARG, ':{') or \
                      match(TokenType.NOT, '~') or \
                      match(TokenType.XOR, '$') or \
                      match(TokenType.ADD, '+') or\
                      match(TokenType.SUB, '-') or\
                      match(TokenType.MUL, '*') or \
                      match(TokenType.DIV, '/') or \
                      match(TokenType.LPAR, '(') or \
                      match(TokenType.RPAR, ')') or \
                      match(TokenType.EXP, '^') or \
                      match(TokenType.TERM, '.') or \
                      match(TokenType.GT, '>') or \
                      match(TokenType.LT, '<') or \
                      match(TokenType.EQ, '=') or \
                      match(TokenType.RARG, '}') or \
                      match(TokenType.SEPARG, ';')
            # print('<' + self.stream + '>')
        yield Token(TokenType.EOF)



if __name__ == '__main__':
    print(Token(TokenType.NUM, 5))
    print(Token(TokenType.LPAR))

    tok = Tokenizer('(x>3) => {{ number :- 4; }} !! {{ number :- 7; }}')
    print(list(tok.tokens()))
    tok = Tokenizer('print:{"Hello", x}')
    print(list(tok.tokens()))

