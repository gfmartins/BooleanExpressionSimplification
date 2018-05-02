import string
from operator import or_, and_, not_, xor
from itertools import product, combinations


def imp(a, b):
    return not a or b


def dys(a, b):
    return not (a and b)


VARS = string.ascii_lowercase
OPS = "~^&|/>"
CONST = "FT"

PREC = {'~': 4,
        '^': 3,
        '&': 2,
        '|': 2,
        '/': 2,
        '>': 1
        }

ASSO = {'&': 'right',
        '/': 'right',
        '>': 'right',
        '^': 'right',
        '|': 'right',
        '~': 'left'}

FUN_OPS = {"|": or_, "&": and_, ">": imp, "~": not_, "^": xor, "/": dys}


def main():
    f = open("dane", "r")
    dane = f.read().splitlines()
    f.close()
    for e in dane:
        if validate(e):
            e = parse(e)
            print(e, " ", simplify(e))
        else:
            print("ERROR")


def simplify(expression):
    v = get_arguments_list(expression)
    o = get_args_that_give_logic_one(expression)
    a = get_minimal_valid_subset(reduce(o), o)
    sum_of_products = print_sum_of_products(a, v)
    if give_the_same_logic_value(expression, sum_of_products):
        infix = sum_of_products
    else:
        infix = expression
    postfix = convert_infix_to_postfix(infix)
    prefix = convert_postfix_to_prefix(postfix)
    use_xor = find_xor(prefix)
    use_implication = "".join(find_implications(prefix))
    candidates = [expression, sum_of_products, use_xor, use_implication]
    result = [(e, len(e)) for e in candidates if give_the_same_logic_value(expression, e)]
    result.sort(key=lambda tup: tup[1])
    return result[0][0]


def find_the_shortest(quin, xo, implication):
    a = [quin, xo, implication]
    a = [(quin, len(quin)), (xo, len(xo)), (implication, len(implication))]
    a.sort(key=lambda tup: tup[1])  # sorts in place
    return a


def validate(expression):
    """"checks syntactic correctness"""
    state = True  # True - we expect '(' or VARS or '~' or CONST, False - we expect ')' or OPS
    par_count = 0  # parenthesis counter
    for char in expression:
        if char == " ":
            continue
        if state:
            if char in VARS or char in CONST:
                state = False
            elif char == "(":
                par_count += 1
            elif char != "~":
                return False
        else:
            if char in OPS:
                state = True
            elif char == ")":
                par_count -= 1
            else:
                return False
        if par_count < 0:  # try to close parenthesis that doesn't exist
            return False
    return par_count == 0 and not state


def parse(expression):
    return expression.replace(" ", "")


def convert_infix_to_postfix(expression):
    """"converts infix to rpn"""
    output = ""
    op_stack = []

    for token in expression:
        if token in VARS or token in CONST:
            output += token
        if token in OPS:
            while op_stack and op_stack[-1] != "(" and (PREC[op_stack[-1]] > PREC[token]
                                                        or PREC[op_stack[-1]] > PREC[token]
                and ASSO[op_stack[-1]] == "left"):
                output += op_stack.pop()
            op_stack.append(token)
        if token == "(":
            op_stack.append(token)
        if token == ")":
            while op_stack[-1] != "(":
                output += op_stack.pop()
            op_stack.pop()
        # print(output)
    while op_stack:
        output += op_stack.pop()
    return output


def get_arguments_list(expression):
    return sorted(set([x for x in expression if x in VARS]))


def map_variable_to_values(rpn_expression, values):
    """"replaces variables present in rpn_expression with values appropriate in terms of order"""
    valued_rpn_expression = ""
    variables = get_arguments_list(rpn_expression)
    var_to_val = dict(zip(variables, values))
    for token in rpn_expression:
        if token in VARS:
            valued_rpn_expression += var_to_val[token]
        elif token == "T":
            valued_rpn_expression += '1'
        elif token == "F":
            valued_rpn_expression += '0'
        else:
            valued_rpn_expression += token
    return valued_rpn_expression


def generate_all_possible_values(expression):
    """"returns list of all possible variations values that can be passed to expression"""
    variables_amount = len(set([x for x in expression if x in VARS]))  # amount of different variables
    return list(map(lambda t: "".join(t), list(product(['0', '1'], repeat=variables_amount))))


def evaluate_rpn_expression(rpn_expression, values):
    """"returns the value of rpn_expression with these particular values passed as arguments"""
    valued_rpn_expression = map_variable_to_values(rpn_expression, values)
    str_to_bool = lambda s: True if s == "1" else False
    bool_to_str = lambda b: "1" if b else "0"
    stack = []
    for token in valued_rpn_expression:
        if token == "~":
            var = str_to_bool(stack.pop())
            res = bool_to_str(FUN_OPS["~"](var))
        elif token in OPS and token != "~":
            var2 = str_to_bool(stack.pop())
            var1 = str_to_bool(stack.pop())
            res = bool_to_str(FUN_OPS[token](var1, var2))
        else:
            res = token
        stack.append(res)
    return str_to_bool(stack.pop())


def merge(s1, s2):
    result = ""
    counter = 0  # changes counter
    for i in range(len(s1)):
        if s1[i] == s2[i]:
            result += s1[i]
        else:
            result += "-"
            counter += 1
    if counter == 1:
        return result
    return False


def reduce(dane):
    result = set()
    b2 = False
    for e1 in dane:
        b1 = False
        for e2 in dane:
            w = merge(e1, e2)
            if w:
                result.add(w)
                b1 = b2 = True
        if not b1:
            result.add(e1)
    if b2:
        return reduce(result)
    return result


def can_create(s1, s2):
    """"checks if strings are the same provided that '-' can be both '0' and '1'"""
    for i in range(len(s2)):
        if s1[i] != '-' and s1[i] != s2[i]:
            return False
    return True


def get_minimal_valid_subset(min_products, arguments):
    min_products_to_args = dict()
    for min_product in min_products:
        min_products_to_args[min_product] = set([x for x in arguments if can_create(min_product, x)])
    for k in range(1, len(min_products) + 1):
        k_elem_min_products_subsets = set(combinations(min_products, k))
        for min_products_subset in k_elem_min_products_subsets:
            args = set()
            for min_product in min_products_subset:
                args = args | min_products_to_args[min_product]
            if len(args) == len(arguments):
                return list(min_products_subset)
    return []


def get_args_that_give_logic_one(expression):
    args = generate_all_possible_values(expression)
    rpn_expression = convert_infix_to_postfix(expression)
    return [a for a in args if evaluate_rpn_expression(rpn_expression, a)]


def print_sum_of_products(expression, variables):
    if not expression:
        return 'F'
    output = []
    for pro in expression:
        s = ""
        for i in range(len(variables)):
            if pro[i] == '1':
                s += variables[i]
            elif pro[i] == '0':
                s += '~' + variables[i]
        output.append(s)
    if output[0] == "":
        return 'T'
    output = add_operators(output, '|')
    res = []
    for pro in output:
        res += add_operators(pro, '&')
    return "".join(res)


def add_operators(expression, operator):
    out = []
    for i in range(len(expression)):
        out.append(expression[i])
        if i != len(expression)-1 and expression[i] != '~':
            out.append(operator)
    return out


def convert_postfix_to_prefix(postfix_expression):
    stack = []
    for token in postfix_expression:
        if token in VARS or token in CONST:
            stack.append(token)
        elif token == '~':
            c = stack.pop()
            stack.append(['~', c])
        elif token in OPS:
            c = stack.pop()
            d = stack.pop()
            stack.append([token, d, c])
    return stack[0]


def find_implications(prefix_expression):
    if len(prefix_expression) != 3:
        return convert_prefix_to_infix(list(flatten(prefix_expression)))
    if prefix_expression[0] == '|':
        if len(prefix_expression[1]) == 2 and len(prefix_expression[2]) != 2:
            return [find_implications(prefix_expression[1][1]), '>', find_implications(prefix_expression[2])]
        elif len(prefix_expression[1]) != 2 and len(prefix_expression[2]) == 2:
            return [find_implications(prefix_expression[2][1]), '>', find_implications(prefix_expression[1])]
        else:
            return convert_prefix_to_infix(list(flatten(prefix_expression)))
    else:
        return convert_prefix_to_infix(list(flatten(prefix_expression)))


def flatten(iterable):
    for elm in iterable:
        if isinstance(elm, (list, tuple)):
            for relm in flatten(elm):
                yield relm
        else:
            yield elm


def has_the_same_variables(e1, e2):
    return get_arguments_list(e1) == get_arguments_list(e2)


def find_xor(prefix_expression):
    if len(prefix_expression) != 3:
        return convert_prefix_to_infix(list(flatten(prefix_expression)))
    elif prefix_expression[0] != '|':
        return convert_prefix_to_infix(list(flatten(prefix_expression)))
    if not has_the_same_variables(flatten(prefix_expression[1]), flatten(prefix_expression[2])):
        return convert_prefix_to_infix(list(flatten(prefix_expression)))
    if len(prefix_expression[1]) != 3 or len(prefix_expression[2]) != 3:
        return convert_prefix_to_infix(list(flatten(prefix_expression)))
    if prefix_expression[1][0] != '&' or prefix_expression[2][0] != '&':
        return convert_prefix_to_infix(list(flatten(prefix_expression)))
    pairs = []
    for i in range(1, 3):
        for j in range(1, 3):
            if are_negation(prefix_expression[1][i], prefix_expression[2][j]):
                pairs.append((i, j))
    if len(pairs) != 2:
        return convert_prefix_to_infix(list(flatten(prefix_expression)))
    res = [prefix_expression[1][1], prefix_expression[1][2]]
    res = list(map(lambda e: e[1] if e[0] == '~' else e, res))
    res = list(map(lambda e: e if len(e) == 1 else "".join(['(', find_xor(e), ')']), res))
    return "".join(res[0] + '^' + res[1])


def are_negation(prefix_expression1, prefix_expression2):
    pre1 = list(flatten(prefix_expression1))
    pre2 = list(flatten(prefix_expression2))
    if not has_the_same_variables(pre1, pre2):
        return False
    pos1 = convert_prefix_to_postfix(pre1)
    pos2 = convert_prefix_to_postfix(pre2)
    for ar in generate_all_possible_values(pos1):
        if evaluate_rpn_expression(pos1, ar) == evaluate_rpn_expression(pos2, ar):
            return False
    return True


def give_the_same_logic_value(exp1, exp2):
    pos1 = convert_infix_to_postfix(exp1)
    pos2 = convert_infix_to_postfix(exp2)
    for ar in generate_all_possible_values(pos1):
        if evaluate_rpn_expression(pos1, ar) != evaluate_rpn_expression(pos2, ar):
            return False
    return True


def convert_prefix_to_postfix(prefix_expression):
    s = []
    for token in prefix_expression[::-1]:
        if token in VARS or token in CONST:
            out = token
        elif token == '~':
            o1 = s.pop()
            out = o1 + token
        elif token in OPS:
            o1 = s.pop()
            o2 = s.pop()
            out = o1 + o2 + token
        s.append(out)
    return s[0]


def convert_prefix_to_infix(prefix_expression):
    s = []
    for token in prefix_expression[::-1]:
        if token in VARS or token in CONST:
            out = token
        elif token == '~':
            o1 = s.pop()
            out = token + o1
        elif token in OPS:
            o1 = s.pop()
            o2 = s.pop()
            out = o1 + token + o2
        s.append(out)
    return s[0]


if __name__ == "__main__":
    main()


