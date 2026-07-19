from abc import ABC
from ortools.sat.python import cp_model


class VarType(ABC):
    def __add__(self, other):
        return VarAdd(self, other)

    def __mul__(self, other):
        return VarMul(self, other)

class VarMul(VarType):
    def __init__(self, var, othervar):
        self.var = var
        self.othervar = othervar

class VarAdd(VarType):
    def __init__(self, var, othervar):
        self.var = var
        self.othervar = othervar

class VarNormal(VarType):
    def __init__(self, idx):
        self.idx = idx

class VarConst(VarType):
    def __init__(self, v):
        self.v = v

class VarGenerator:
    def __init__(self, cnt):
        self.model = cp_model.CpModel()
        self.vars = []
        for _ in range(cnt):
            self._new_var()
        self.model.add_all_different(self.vars)

    def _new_var(self, _max = 100):
        self.vars.append(self.model.new_int_var(1, _max, f"v[{len(self.vars) + 1}]"))
        return self.vars[-1]

    def add(self, expr1, expr2):
        self.model.add(self.convert(expr1) == self.convert(expr2))

    def convert(self, expr):
        # print('convert', expr)
        if isinstance(expr, VarNormal):
            return self.vars[expr.idx]

        elif isinstance(expr, VarConst):
            return expr.v

        elif isinstance(expr, VarAdd):
            first = self.convert(expr.var)
            second = self.convert(expr.othervar)
            tmp = self._new_var(1000000)

            # print(f'{tmp} = {first} + {second}')
            self.model.add(tmp == first + second)
            return tmp

        elif isinstance(expr, VarMul):
            first = self.convert(expr.var)
            second = self.convert(expr.othervar)
            tmp = self._new_var(1000000)

            # print(f'{tmp} = {first} * {second}')
            self.model.add_multiplication_equality(
                tmp, [first, second]
            )
            return tmp

# EPSILON = 0.000001
class SolutionSearcher(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables: list[cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables = variables
        self.solution_count = 0

    def on_solution_callback(self):
        result = list(map(
            lambda v: self.value(v),
            self.variables[0:40]
        ))

        _max = max(result)
        mean = sum(result) / 40
        so = sorted(result)
        median = (so[19] + so[20]) / 2
        s = sum(map(
            lambda x: x*x, map(
                lambda y: y - mean, result
            )
        )) / 40

        ans = _max * mean * median * s
        # if abs(round(ans) - ans) < EPSILON:
        #     self.solution_count += 1
        #     print(f'#{self.solution_count}', round(ans))
        #     print(result)
        # else:
        #     return
        self.solution_count += 1
        print(f'#{self.solution_count}', ans)
        print(result)


def solve():
    gen = VarGenerator(40)
    
    v = lambda i: VarNormal(i-1)
    c = lambda c: VarConst(c)

    # horizontal
    gen.add(v(1)*v(2)+c(4)*v(3), v(4))
    gen.add(v(5)*v(6), v(7)+v(8))
    gen.add(c(6)*v(11), v(12))
    gen.add(c(4)*v(13), v(14))
    gen.add(v(15)+v(17), v(16)+v(18))
    gen.add(v(18), v(19)+c(27))
    gen.add(v(20), v(21)+v(22))
    gen.add(v(23), v(24)+v(25))
    gen.add(v(26)*v(27)+c(4)*v(28), c(4)*v(28)*v(30))
    gen.add(v(31)+v(32), c(23)+v(33))
    gen.add(v(35)+v(36)+v(38), v(37)+v(39)+v(40))
    # vertical
    gen.add(v(1)+v(5)+v(20), c(6)*v(15))
    gen.add(v(1)+v(5)+v(31)+v(35), v(26))
    gen.add(v(2)+v(16), v(6)+v(11)+v(21))
    gen.add(v(27)+c(23), v(36))
    gen.add(c(4)+v(7)+v(12), v(17))
    gen.add(v(22)+c(4)*v(32), c(4)*v(37))
    gen.add(v(3)*v(8)+c(4)*v(18), v(23)*c(4))
    gen.add(v(4)*v(13), v(9)*v(19))
    gen.add(v(24)+v(29)+v(34), v(39))
    gen.add(v(10)+v(14)+c(27), v(25))


    solver = cp_model.CpSolver()
    searcher = SolutionSearcher(gen.vars)
    solver.parameters.enumerate_all_solutions = True
    status = solver.solve(gen.model, searcher)


    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        result = list(map(lambda i: solver.value(gen.vars[i]), range(40)))

        _max = max(result)
        mean = sum(result) / 40
        so = sorted(result)
        median = (so[19] + so[20]) / 2
        s = sum(map(
            lambda x: x*x, map(
                lambda y: y - mean, result
            )
        )) / 40

        print('max:', _max)
        print('mean:', mean)
        print('median:', median)
        print('distribution:', s)

        print('ans:', _max * mean * median * s)

        
        print(result)
        for i in range(len(gen.vars)):
            print(f"var[{i+1}] = {solver.value(gen.vars[i])}")
    else:
        print("no solution found.")

if __name__ == "__main__":
    solve()
