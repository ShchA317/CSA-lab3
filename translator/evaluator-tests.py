from evaluator import evaluate
from reader import lisp_my_ast_builder
from isa import Opcode
from evaluator import create_instr
import json

sExpressions, symbols, _ = lisp_my_ast_builder("(+ 1 (- 3 2))")

code = []
for form in sExpressions:
    machineCodes = []
    prevId = 0
    machineCodes, _, symbols = evaluate(form, machineCodes, 0, symbols)
    code += machineCodes

code.append(create_instr(Opcode.HLT, '', 0))

count = 0
for c in code:
    c["num"] = count
    count += 1

print(json.dumps(code, indent=2))
