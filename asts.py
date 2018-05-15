from tokenizer import Token, TokenType

class ExpressionAST:
    def __init__(self, op, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def __str__(self):
        return f'({self.op} {self.lhs} {self.rhs})'

    def execute(self, scope):
        if self.lhs is None:
            if self.op.type is TokenType.ADD:
                return self.rhs.execute(scope)
            elif self.op.type is TokenType.SUB:
                return -1 * self.rhs.execute(scope)
            elif self.op.type is TokenType.NOT:
                return not self.rhs.execute(scope)
        if self.op.type is TokenType.ADD:
            return self.lhs.execute(scope) + self.rhs.execute(scope)
        if self.op.type is TokenType.SUB:
            return self.lhs.execute(scope) - self.rhs.execute(scope)
        if self.op.type is TokenType.MUL:
            return self.lhs.execute(scope) * self.rhs.execute(scope)
        if self.op.type is TokenType.DIV:
            return self.lhs.execute(scope) / self.rhs.execute(scope)
        if self.op.type is TokenType.EXP:
            return self.lhs.execute(scope) ** self.rhs.execute(scope)
        if self.op.type is TokenType.GT:
            return self.lhs.execute(scope) > self.rhs.execute(scope)
        if self.op.type is TokenType.LT:
            return self.lhs.execute(scope) < self.rhs.execute(scope)
        if self.op.type is TokenType.GE:
            return self.lhs.execute(scope) >= self.rhs.execute(scope)
        if self.op.type is TokenType.LE:
            return self.lhs.execute(scope) <= self.rhs.execute(scope)
        if self.op.type is TokenType.EQ:
            return self.lhs.execute(scope) == self.rhs.execute(scope)


class AtomAST:
    def __init__(self, atom: Token):
        assert atom.type in (TokenType.NUM, TokenType.STR, TokenType.ID)
        self.val = atom.value
        self.type = atom.type

    def __str__(self):
        if self.type == TokenType.ID:
            return f'${self.val}'
        return repr(self.val)

    def execute(self, scope):
        if self.type == TokenType.ID:
            return scope[self.val].execute(scope)
        return self.val


class AssignmentAST:
    def __init__(self, dest, val):
        self.dest = dest
        self.val = val

    def __str__(self):
        return f'[{self.dest} <- {self.val}]'

    def execute(self, scope):
        # scope[self.dest.value] = self.val.execute(scope)
        val = self.val.execute(scope)
        if type(val) is AtomAST:
            scope[self.dest.value] = self.val
        elif type(val) is int:
            scope[self.dest.value] = AtomAST(Token(TokenType.NUM, val))
        elif type(val) is str:
            scope[self.dest.value] = AtomAST(Token(TokenType.STR, val))
        else:
            scope[self.dest.value] = AtomAST(Token(TokenType.STR, val))
            print('Warning: value of type {} is not supported!'.format(type(val)))

        return self.val


class BlockAST:
    def __init__(self, lines):
        self.lines = lines

    def __str__(self):
        return f'[{" ".join(map(str, self.lines))}]'

    def execute(self, scope):
        ret = None
        for line in self.lines:
            ret = line.execute(scope)
        return ret


class ConditionalAST:
    def __init__(self, cond, yes, no):
        self.cond = cond
        self.yes = yes
        self.no = no

    def __str__(self):
        return f'(IF {self.cond} {self.yes} {self.no})'

    def execute(self, scope):
        if self.cond.execute(scope):
            return self.yes.execute(scope)
        return self.no.execute(scope)


class CallAST:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        return f'({self.name.value} {" ".join(map(str, self.args))})'

    def execute(self, scope):
        return scope[self.name.value](self.args, scope)


class FunctionAST:
    def __init__(self, args, body):
        self.scope = dict()
        self.argNames = args
        self.body = body

    def __str__(self):
        return f'(func [{" ".join(self.argNames)}] {self.body}'

    def __call__(self, args, scope):
        # copy global scope
        for k, v in scope.items():
            self.scope[k] = v
        # assign parameter values
        for arg, val in zip(self.argNames, args):
            self.scope[arg] = val

        # call the function with modified local scope
        return self.body.execute(self.scope)
