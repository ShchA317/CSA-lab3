import re
import isa
from ast_classes import *

funcs = {
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

# удаляет комментарии и ужимает код в одну стрку
def minimize(code):
    pattern = r';.*$'
    code = re.sub(pattern, '', code, flags=re.MULTILINE)
    compressed_code = code.replace('\n', '').strip()
    compressed_code = ' '.join(compressed_code.split())
    return compressed_code

def isSelfEvaluated(pred: str) -> bool:
    return pred[0] == '"' or str.isnumeric(pred) or pred == 'NIL' or pred == 'T'


def is_correct_brackets(text):
  breacket_count = 0
  for char in text:
    if char == ")":
      breacket_count -= 1
    if char == "(":
      breacket_count += 1
    if breacket_count < 0:
      return False
  if breacket_count != 0:
    return False
  return True


def readExpressions(text, pos, prevCh):
    sExpressions = []
    sExpr = ''
    isInString = False
    while pos < len(text):
        ch = text[pos]
        if ch == '"':
            if isInString:
                isInString = False
                sExpr += ch
                sExpressions.append(sExpr)
                sExpr = ''
            else:
                isInString = True
                sExpr += ch
        elif (ch in (' ', '\n')) and not isInString:
            if sExpr == '' and (prevCh in (' ', '\n')):
                sExpr = 'NIL'
            if sExpr not in ('', '\n'):
                sExpressions.append(sExpr)
            sExpr = ''
        elif ch == '(':
            sExpr, pos = readExpressions(text, pos + 1, ch)
            prevCh = text[pos]
            sExpressions.append(sExpr)
            sExpr = ''
            pos += 1
            continue
        elif ch == ')':
            if sExpr == '' and (prevCh in (' ', '\n')):
                sExpr = 'NIL'
            if sExpr not in ('', '\n'):
                sExpressions.append(sExpr)
            return sExpressions, pos
        else:
            sExpr += ch
        pos += 1
        prevCh = ch

    return sExpressions, pos, text[pos - 1]


def makeLispForm(expr, symbols: dict, symbAddr: int):
    if isinstance(expr, (LispAtom, LispList)):
        return expr, symbols, symbAddr
    if not isinstance(expr, list):
        s = str(expr)
        form = []
        if s.isnumeric():
          form = LispAtom(int(expr), AtomType.NUM)
        elif s.startswith('"'):
          form = LispAtom(expr[1:-1], AtomType.STRING)
        elif s in {'NIL', 'T'}:
          form = LispAtom(expr, AtomType.CONST)
        elif s in symbols:
          form = LispAtom(expr, AtomType.CHAR)
        else:
          symbols[s] = (AtomType.UNDEF, LispAtom('n', AtomType.UNDEF), symbAddr)
          symbAddr += 1
          form = LispAtom(expr, AtomType.CHAR)

        return form, symbols, symbAddr

    pred = expr[0]
    assert isSelfEvaluated(pred) == False
    assert (pred not in symbols and pred not in funcs) == False

    args = []
    for arg in expr[1:]:
      m = makeLispForm(arg, symbols, symbAddr)
      args.append(m[0])
      symbols = m[1]
      symbAddr = m[2]

    form = LispList(pred, funcs.get(pred), args)

    return form, symbols, symbAddr


def showSymbols(symbols):
    print("{")
    for k in symbols:
        print(f'{k}: <{symbols.get(k)[0]}> {symbols.get(k)[1].content}')
    print("}")
    print()



# [reader]
def lispMyASTBuilder(text):
    symbols = {}
    symbAddr = 100
    forms = []

    text = minimize(text)
    if is_correct_brackets(text):
        sExpressions = readExpressions(text, 0, 'a')
        for expr in sExpressions[0]:
            form, symbols, symbAddr = makeLispForm(expr, symbols, symbAddr)
            forms.append(form)
    else:
        print('')
    return forms, symbols, symbAddr