# coding=utf-8

from tokenizer import Tokenizer
from lexer import Lexer


# define builtin functions
def builtin_print(args, inj_scope):
    params = [arg.execute(inj_scope) for arg in args]
    print(*params)

def builtin_prompt(args, inj_scope):
    return input(args[0].execute(inj_scope))

"""
{{
    x :- prompt:{"Enter a number: ";}.
    


"""

scope = {
    'print': builtin_print,
    'prompt': builtin_prompt
}
if __name__ == '__main__':
    while True:
        import sys
        print('[Sapphire]')
        read = sys.stdin.readlines()
        # read = """{{
	# x :- 10.
	# y :- 15.
	# (x > y) => print:{"X is bigger";} !! print:{"Y is bigger";}.
# }}
# """.split()
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