# coding=utf-8
from tokenizer import *
from asts import *


"""
atom = num | id
"""

"""
expr = atom | (expr) | expr op expr
"""


# class Lexer:
#     def __init__(self, tokens: List[Token]):
#         self.tokens = tokens
#
#     def peek(self, tok: TokenType) -> bool:
#         return self.tokens[0].type == tok
#
#     def atom(self):
#         try:
#             ast = AtomAST(self.tokens[0])
#             del self.tokens[0]
#             return ast
#         except AssertionError:
#             return False
#
#     def expression(self):
#         if self.peek(TokenType.LPAR):
#             del self.tokens[0]
#             ast = self.expression()
#             if self.peek(TokenType.RPAR):
#                 return ast
#             raise Exception("Expected ')'!")
#

class Lexer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.ptr = 0
        self.saved = list()
        self.parsed = None

    def save(self):
        self.saved.append(self.ptr)

    def reset(self):
        self.ptr = self.saved.pop()

    def eat(self, tok):
        if self.tokens[self.ptr].type == tok or (type(tok) is not TokenType and self.tokens[self.ptr].type in tok):
            self.ptr += 1
            return self.tokens[self.ptr - 1]
        raise TokenError(f'Expected {tok}')

    def expect(self, tok):
        raise TokenError(f'Expected {tok}, received {self.tokens[self.ptr].type}')

    def atom(self):
        try:
            self.save()
            tok = self.eat(TokenType.STR)
            self.saved.pop()
            return AtomAST(tok)
        except TokenError:
            self.reset()

        try:
            self.save()
            tok = self.eat(TokenType.NUM)
            self.saved.pop()
            return AtomAST(tok)
        except TokenError:
            self.reset()

        try:
            self.save()
            return AtomAST(self.eat(TokenType.ID))
        except TokenError:
            self.reset()

        self.expect('atom')

    def expression(self):
        def thing():
            try:
                self.save()
                unop = self.eat((TokenType.ADD, TokenType.SUB))
                rhs = self.expression()
                self.saved.pop()
                return ExpressionAST(unop, None, rhs)
            except TokenError:
                self.reset()

            try:
                self.save()
                self.eat(TokenType.LPAR)
                expr = self.expression()
                self.eat(TokenType.RPAR)
                self.saved.pop()
                return expr
            except TokenError:
                self.reset()

            try:
                self.save()
                atom = self.atom()
                self.saved.pop()
                return atom
            except TokenError:
                self.reset()

            self.expect('atom or (expression)')

        def exps():
            ast = thing()
            while self.tokens[self.ptr].type == TokenType.EXP:
                op = self.eat(TokenType.EXP)
                rhs = thing()
                ast = ExpressionAST(op, ast, rhs)
            return ast

        def muldiv():
            ast = exps()
            while self.tokens[self.ptr].type in (TokenType.MUL, TokenType.DIV):
                op = self.eat((TokenType.MUL, TokenType.DIV))
                rhs = exps()
                ast = ExpressionAST(op, ast, rhs)
            return ast

        try:
            self.save()
            ast = muldiv()
            while self.tokens[self.ptr].type in (TokenType.ADD, TokenType.SUB):
                op = self.eat((TokenType.ADD, TokenType.SUB))
                rhs = muldiv()
                ast = ExpressionAST(op, ast, rhs)
            self.saved.pop()
            return ast
        except TokenError:
            self.reset()

        self.expect('expression')

    def assignment(self):
        dest = self.eat(TokenType.ID)
        self.eat(TokenType.ASSIGN)
        val = self.line()
        return AssignmentAST(dest, val)

    def boolean(self):
        def singleBool():
            try:
                self.save()
                unop = self.eat(TokenType.NOT)
                rhs = self.boolean()
                self.saved.pop()
                return ExpressionAST(unop, None, rhs)
            except TokenError:
                self.reset()

            try:
                self.save()
                self.eat(TokenType.LPAR)
                boolean = self.boolean()
                self.eat(TokenType.RPAR)
                self.saved.pop()
                return boolean
            except TokenError:
                self.reset()

            try:
                self.save()
                lhs = self.expression()
                op = self.eat((TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.EQ))
                rhs = self.expression()
                self.saved.pop()
                return ExpressionAST(op, lhs, rhs)
            except TokenError:
                self.reset()

            self.expect('boolean')

            # try:
            #     self.save()
            #     return self.expression()
            # except TokenError:
            #     self.reset()

        def ands():
            ast = singleBool()
            while self.tokens[self.ptr].type == TokenType.AND:
                op = self.eat(TokenType.AND)
                rhs = singleBool()
                ast = ExpressionAST(op, ast, rhs)
            return ast

        def xors():
            ast = ands()
            while self.tokens[self.ptr].type == TokenType.XOR:
                op = self.eat(TokenType.XOR)
                rhs = ands()
                ast = ExpressionAST(op, ast, rhs)
            return ast

        try:
            self.save()
            ast = xors()
            while self.tokens[self.ptr].type == TokenType.OR:
                op = self.eat(TokenType.OR)
                rhs = xors()
                ast = ExpressionAST(op, ast, rhs)
            self.saved.pop()
            return ast
        except TokenError:
            self.reset()

        self.expect('boolean')

    def conditional(self):
        try:
            self.save()
            cond = self.boolean()
            self.eat(TokenType.THEN)
            yes = self.line()
            no = None
            if self.tokens[self.ptr].type is TokenType.ELSE:
                self.eat(TokenType.ELSE)
                no = self.line()
            self.saved.pop()
            return ConditionalAST(cond, yes, no)
        except TokenError:
            self.reset()

        try:
            self.save()
            cond = self.expression()
            self.eat(TokenType.THEN)
            yes = self.line()
            no = None
            if self.tokens[self.ptr].type is TokenType.ELSE:
                self.eat(TokenType.ELSE)
                no = self.line()
            self.saved.pop()
            return ConditionalAST(cond, yes, no)
        except TokenError:
            self.reset()

        self.expect('conditional')

    def callFunc(self):
        name = self.eat(TokenType.ID)
        self.eat(TokenType.LARG)
        args = list()
        while self.tokens[self.ptr].type is not TokenType.RARG:
            args.append(self.line())
            if self.tokens[self.ptr].type is TokenType.SEPARG:
                self.eat(TokenType.SEPARG)
            else:
                break
        self.eat(TokenType.RARG)

        return CallAST(name, args)

    def line(self):
        try:
            self.save()
            self.eat(TokenType.LBLK)
            lines = list()
            while self.tokens[self.ptr].type is not TokenType.RBLK:
                lines.append(self.line())
                self.eat(TokenType.TERM)
            self.eat(TokenType.RBLK)
            return BlockAST(lines)
        except TokenError:
            self.reset()

        try:
            self.save()
            return self.callFunc()
        except TokenError:
            self.reset()

        try:
            self.save()
            return self.conditional()
        except TokenError:
            self.reset()

        try:
            self.save()
            return self.assignment()
        except TokenError:
            self.reset()

        try:
            self.save()
            return self.boolean()
        except TokenError:
            self.reset()

        try:
            self.save()
            return self.expression()
        except TokenError:
            self.reset()

        self.expect('assignment or expression')





# def execute(ast):
#     if type(ast) is AssignmentAST:
#         variables[ast.dest.value] = ast.val
#         return ast.val
#     elif type(ast) is ExpressionAST:
#         if ast.lhs is None:
#             if ast.op.type == TokenType.SUB:
#                 return -1 * int(execute(ast.rhs))
#             elif ast.op.type == TokenType.ADD:
#                 return int(execute(ast.rhs))
#             elif ast.op.type == TokenType.NOT:
#                 return not execute(ast.rhs)
#         if ast.op.type == TokenType.ADD:
#             return execute(ast.lhs) + execute(ast.rhs)
#         elif ast.op.type == TokenType.SUB:
#             return execute(ast.lhs) - execute(ast.rhs)
#         elif ast.op.type == TokenType.MUL:
#             return execute(ast.lhs) * execute(ast.rhs)
#         elif ast.op.type == TokenType.DIV:
#             return execute(ast.lhs) / execute(ast.rhs)
#         elif ast.op.type == TokenType.EXP:
#             return execute(ast.lhs) ** execute(ast.rhs)
#         elif ast.op.type == TokenType.GT:
#             return execute(ast.lhs) > execute(ast.rhs)
#         elif ast.op.type == TokenType.LT:
#             return execute(ast.lhs) < execute(ast.rhs)
#         elif ast.op.type == TokenType.GE:
#             return execute(ast.lhs) >= execute(ast.rhs)
#         elif ast.op.type == TokenType.LE:
#             return execute(ast.lhs) <= execute(ast.rhs)
#         elif ast.op.type == TokenType.EQ:
#             return execute(ast.lhs) == execute(ast.rhs)
#     elif type(ast) is AtomAST:
#         if ast.type == TokenType.ID:
#             return execute(variables[ast.val])
#         else:
#             return ast.val
#     elif type(ast) is BlockAST:
#         val = None
#         for line in ast.lines:
#             val = execute(line)
#         return val
#     elif type(ast) is ConditionalAST:
#         if execute(ast.cond):
#             return execute(ast.yes)
#         elif ast.no is not None:
#             return execute(ast.no)
#



if __name__ == '__main__':
    # 3 * (5 + x)
    # ast = ExpressionAST(TokenType.MUL, AtomAST(Token(TokenType.NUM, 3)),
    #                     ExpressionAST(TokenType.ADD, AtomAST(Token(TokenType.NUM, 5)),
    #                                   AtomAST(Token(TokenType.ID, 'x'))))
    #
    # print(ast)



    while True:
        import sys
        print('[Sapphire]')

        expression = ' '.join(map(str.strip, sys.stdin.readlines()))
        print(expression)
        # expression = input('$ ')
        # expression = '3 + 4'
        if expression == 'quit':
            break
        toks = list(Tokenizer(expression).tokens())
        print(toks)
        lex = Lexer(toks)
        ast = lex.line()
        print(ast)
        # print(f'=> {execute(ast)}')
        print(f'=> {ast.execute(variables)}')
        # print(variables)

