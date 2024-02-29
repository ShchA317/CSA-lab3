from evaluator import evaluate
from reader import lispMyASTBuilder
from isa import Opcode
from evaluator import createInstr
import json

sExpressions, symbols, _ = lispMyASTBuilder("(+ 1 2 3)")

code = []
for form in sExpressions:
    machineCodes = []
    prevId = 0
    machineCodes, _, symbols = evaluate(form, machineCodes, 0, symbols)
    code += machineCodes

code.append(createInstr(Opcode.HLT, '', 0))
print(json.dumps(code, indent=4))
