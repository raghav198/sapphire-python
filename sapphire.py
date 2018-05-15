# coding=utf-8

from tokenizer import *
from lexer import Lexer
import sys


# define builtin functions
def builtin_print(args, inj_scope):
    params = [arg.execute(inj_scope) for arg in args]
    print(*params)


def builtin_prompt(args, inj_scope):
    # return AtomAST(Token(TokenType.STR, input(args[0].execute(inj_scope))))
    inp = input(args[0].execute(inj_scope))
    if len(args) == 1:
        args.append('str')
    else:
        args[1] = args[1].execute(inj_scope)
    if type(eval(args[1])) is not type:
        print('{} is not a valid coercion type; returning as string')
        args[1] = 'str'
    return eval(args[1])(inp)

"""
{{
    x :- prompt:{"Enter a number: ";}.
    


"""

scope = {
    'print': builtin_print,
    'prompt': builtin_prompt
}
if __name__ == '__main__':
    sys.argv.append('script.sfr')
    while True:

        print('[Sapphire]')
        if len(sys.argv) > 1:
            read = open(sys.argv[1]).readlines()
        else:
            read = sys.stdin.readlines()

        expression = ' '.join(map(str.strip, read))
        # print(expression)
        # expression = input('$ ')
        # expression = '3 + 4'
        if expression == 'quit':
            break
        # for tok in Tokenizer(expression).tokens(True):
        #     print(tok)
        toks = list(Tokenizer(expression).tokens())
        # print(toks)
        lex = Lexer(toks)
        ast = lex.line()
        # print(ast)
        # print(f'=> {execute(ast)}')
        print(f'=> {ast.execute(scope)}')
        # print(scope)
        if len(sys.argv) > 1:
            break
