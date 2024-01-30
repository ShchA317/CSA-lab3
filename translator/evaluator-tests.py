import evaluator

sExpressions, symbols, _ = readerWork(text)

code = []
for form in sExpressions:
    machineCodes = []
    prevId = 0
    machineCodes, _, symbols = evaluate(form, machineCodes, 0, symbols)
    code += machineCodes

code.append(createInstr(Opcode.HLT, '', 0))
print(code)
