import re
from ast_classes import *

funcs = {
    'scan': ListType.FUNC,
    'print': ListType.FUNC,
    '+': ListType.FUNC,
    '-': ListType.FUNC,
    '*': ListType.FUNC,
    ':': ListType.FUNC,
    'mod': ListType.FUNC,
    'rem': ListType.FUNC,
    '=': ListType.FUNC,
    '!=': ListType.FUNC,
    '>': ListType.FUNC,
    '>=': ListType.FUNC,
    'set': ListType.SPEC,
    'loop': ListType.SPEC,
    'return': ListType.SPEC,
    'if': ListType.SPEC,
}


def minimize(code):
    pattern = r';.*$'
    code = re.sub(pattern, '', code, flags=re.MULTILINE)
    compressed_code = code.replace('\n', '').strip()
    compressed_code = ' '.join(compressed_code.split())
    return compressed_code


def is_self_evaluated(pred: str) -> bool:
    return pred[0] == '"' or str.isnumeric(pred) or pred == 'NIL' or pred == 'T'


def is_correct_brackets(text):
    bracket_count = 0
    for char in text:
        if char == ")":
            bracket_count -= 1
        if char == "(":
            bracket_count += 1
        if bracket_count < 0:
            return False
    if bracket_count != 0:
        return False
    return True


def read_expressions(text, pos, prev_ch):
    s_expressions = []
    s_expr = ''
    is_in_string = False
    while pos < len(text):
        ch = text[pos]
        if ch == '"':
            if is_in_string:
                is_in_string = not is_in_string
                s_expr += ch
                s_expressions.append(s_expr)
                s_expr = ''
            else:
                is_in_string = not is_in_string
                s_expr += ch
        elif (ch in (' ', '\n')) and not is_in_string:
            if s_expr == '' and (prev_ch in (' ', '\n')):
                s_expr = 'NIL'
            if s_expr not in ('', '\n'):
                s_expressions.append(s_expr)
            s_expr = ''
        elif ch == '(':
            s_expr, pos = read_expressions(text, pos + 1, ch)
            prev_ch = text[pos]
            s_expressions.append(s_expr)
            s_expr = ''
            pos += 1
            continue
        elif ch == ')':
            if s_expr == '' and (prev_ch in (' ', '\n')):
                s_expr = 'NIL'
            if s_expr not in ('', '\n'):
                s_expressions.append(s_expr)
            return s_expressions, pos
        else:
            s_expr += ch
        pos += 1
        prev_ch = ch

    return s_expressions, pos, text[pos - 1]


def make_lisp_form(expr, symbols: dict, symb_addr: int):
    if isinstance(expr, (LispAtom, LispList)):
        return expr, symbols, symb_addr
    if not isinstance(expr, list):
        s = str(expr)
        if s.isnumeric():
            form = LispAtom(int(expr), AtomType.NUM)
        elif s.startswith('"'):
            form = LispAtom(expr[1:-1], AtomType.STRING)
        elif s in {'NIL', 'T'}:
            form = LispAtom(expr, AtomType.CONST)
        elif s in symbols:
            form = LispAtom(expr, AtomType.CHAR)
        else:
            symbols[s] = (AtomType.UNDEF, LispAtom('n', AtomType.UNDEF), symb_addr)
            symb_addr += 1
            form = LispAtom(expr, AtomType.CHAR)

        return form, symbols, symb_addr

    pred = expr[0]
    assert not is_self_evaluated(pred)
    assert not (pred not in symbols and pred not in funcs)

    args = []
    for arg in expr[1:]:
        lisp_form = make_lisp_form(arg, symbols, symb_addr)
        args.append(lisp_form[0])
        symbols = lisp_form[1]
        symb_addr = lisp_form[2]

    form = LispList(pred, funcs.get(pred), args)
    return form, symbols, symb_addr


def lisp_my_ast_builder(text):
    symbols = {}
    symb_addr = 103
    forms = []

    text = minimize(text)
    if is_correct_brackets(text):
        s_expressions = read_expressions(text, 0, '')
        for expr in s_expressions[0]:
            form, symbols, symb_addr = make_lisp_form(expr, symbols, symb_addr)
            forms.append(form)
    return forms, symbols, symb_addr
