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

FUN_OPS = {"|": or_, "&": and_, ">": imp, "~": not_, "^": xor, "/":  dys}


def main():
    f = open("dane", "r")
    dane = f.read().splitlines()
    f.close()
    for e in dane:
        a = get_minimal_valid_subset(reduce(get_args_that_give_one(e)), get_args_that_give_one(e))
        print(e, "   ", a)
    k = "(a|b)|(c|a|b)"
    l = get_minimal_valid_subset(reduce(get_args_that_give_one(k)), get_args_that_give_one(k))
    print(l)
    

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


def convert_to_rpn(expression):
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
    while op_stack:
        output += op_stack.pop()
    return output


def map_variable_to_values(rpn_expression, values):
    """"replaces variables present in rpn_expression with values appropriate in terms of order"""
    valued_rpn_expression = ""
    variables = sorted(set([x for x in rpn_expression if x in VARS]))
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
        # print(stack)
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
        # print(k)
        k_elem_min_products_subsets = set(combinations(min_products, k))
        for min_products_subset in k_elem_min_products_subsets:
            # print("produkt ", list(min_products_subset))
            args = set()
            for min_product in min_products_subset:

                args = args | min_products_to_args[min_product]
                # print(list(args))
            if len(args) == len(arguments):
                return min_products_subset
    return False


def get_args_that_give_one(expression):
    args = generate_all_possible_values(expression)
    rpn_expression = convert_to_rpn(expression)
    return [a for a in args if evaluate_rpn_expression(rpn_expression, a)]


if __name__ == "__main__":
    main()
