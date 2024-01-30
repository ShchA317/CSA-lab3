import sys
# import ast_classes
# from isa import Opcode 

print(sys.version_info)

buffer = 0
prevId = 0
strPointer = 999


def createInstr(op: Opcode, arg, ismem):
    return {
        "opcode": op,
        "arg": arg,
        "mem": ismem
    }


def loadValue(value: LispAtom, symbols) -> list:
    loadingValue = 0
    machineCodes = []
    if value.type == AtomType.CHAR:
        address = symbols[value.content][2]
        machineCodes.append(createInstr(Opcode.LOAD, address, 1))
        return machineCodes
    if value.type == AtomType.CONST:
        if value.content == 'T':
            loadingValue = 1
        else:
            loadingValue = 0
    elif value.type == AtomType.PREV:
        address = int(value.content)
        machineCodes.append(createInstr(Opcode.LOAD, address, 1))
        return machineCodes
    elif value.type == AtomType.STRING:
        loadingValue = ord(value.content)
    else:
        loadingValue = value.content

    machineCodes.append(createInstr(Opcode.LOAD, loadingValue, 0))
    return machineCodes


def storeValue(value: LispAtom, symbols) -> list:
    machineCodes = []
    if value.type == AtomType.CHAR:
        address = symbols[value.content][2]
        machineCodes.append(createInstr(Opcode.STORE, address, 1))
        return machineCodes
    if value.type == AtomType.NUM:
        machineCodes.append(createInstr(Opcode.STORE, value.content, 1))
    elif value.type == AtomType.PREV:
        machineCodes.append(createInstr(Opcode.STORE, value.content, 1))
    return machineCodes


def storeString(value: LispAtom, symbols) -> list:
    assert value.type == AtomType.STRING
    machineCodes = []
    global strPointer
    value.content += '\0'
    for ch in reversed(value.content):
        machineCodes += loadValue(LispAtom(ch, AtomType.STRING), symbols)
        machineCodes += storeValue(LispAtom(strPointer, AtomType.NUM), symbols)
        strPointer -= 1
    return machineCodes


def storePrev(prev, symbols):
    return storeValue(LispAtom(prev, AtomType.PREV), symbols)


def lispSetq(form, symbols):
    machineOp = []
    assert len(form.args) == 2
    assert form.args[0].type == AtomType.CHAR
        
    if form.args[0].content in symbols:
        memAddr = symbols[form.args[0].content][2]
        symbols[form.args[0].content] = (AtomType.CONST, constNIL, memAddr)
    if form.args[1].type == AtomType.STRING:
        memAddr = symbols[form.args[0].content][2]
        symbols[form.args[0].content] = (AtomType.STRING, '', memAddr)
    else:
        memAddr = symbols[form.args[0].content][2]
        symbols[form.args[0].content] = (AtomType.CONST, constNIL, memAddr)

    val = form.args[1]
    t = val.type

    if t == AtomType.STRING:
        machineOp = storeString(val, symbols)
        machineOp += loadValue(LispAtom(strPointer + 1, AtomType.NUM), symbols)
        machineOp += storeValue(form.args[0], symbols)
        return machineOp, symbols

    if t == AtomType.CHAR:
        assert val.content in symbols
    for i in loadValue(form.args[1], symbols):
        machineOp.append(i)
    for i in storeValue(form.args[0], symbols):
        machineOp.append(i)
    return machineOp, symbols


def arithCheck(form: LispList, symbols) -> bool:
    assert len(form.args) == 2
    for a in form.args:
        assert a.type != AtomType.CHAR or symbols[a.content][0] != AtomType.UNDEF
        assert isinstance(a, LispAtom)
        assert a.type in (AtomType.CHAR, AtomType.NUM, AtomType.PREV)

        assert a.type != AtomType.CHAR or (symbols[a.content] == 'NIL'
                                            and symbols[a.content] != constNIL
                                            and symbols[a.content][0] != AtomType.CONST
                                            and symbols[a.content][0] != AtomType.NUM)
            
    return True


def lispArith(form: LispList, symbols):
    if not arithCheck(form, symbols):
        return []

    machineCodes = []

    for instr in loadValue(form.args[0], symbols):
        machineCodes.append(instr)

    code = Opcode.ADD
    if form.content == 'rem':
        code = Opcode.REM
    elif form.content == 'mod':
        code = Opcode.MOD
    elif form.content == '-':
        code = Opcode.SUB
    if form.args[1].type == AtomType.PREV:
        machineCodes.append(createInstr(code, int(form.args[1].content), 1))
    elif form.args[1].type == AtomType.CHAR:
        machineCodes.append(createInstr(code, symbols[form.args[1].content][2], 1))
    else:
        machineCodes.append(createInstr(code, form.args[1].content, 0))
    # machineCodes += storeValue(form.args[0])
    return machineCodes


def lispPrint(form: LispList, symbols):
    assert len(form.args) == 1
    for a in form.args:
        print(a.content)
        if a.type == AtomType.CHAR and symbols[a.content][0] == AtomType.UNDEF:
          assert False
        assert isinstance(a, LispAtom)==True
        assert a.type in (AtomType.CHAR, AtomType.NUM, AtomType.PREV)
            
        if a.type == AtomType.CHAR and not (symbols[a.content][0] == AtomType.STRING
                                            or symbols[a.content] == 'NIL'
                                            or symbols[a.content] == constNIL
                                            or symbols[a.content][0] == AtomType.CONST
                                            or symbols[a.content][0] == AtomType.NUM):
          assert False
            

    machineCodes = []
    if form.args[0].type == AtomType.CHAR and symbols[form.args[0].content][0] == AtomType.STRING:
        memAddr = symbols[form.args[0].content][2]
        machineCodes.append(createInstr(Opcode.LOAD, memAddr, 2))
        machineCodes.append(createInstr(Opcode.PRINT, '', 0))

        machineCodes.append(createInstr(Opcode.LOAD, memAddr, 1))
        machineCodes.append(createInstr(Opcode.ADD, 1, 0))
        machineCodes.append(createInstr(Opcode.STORE, memAddr, 1))

        machineCodes.append(createInstr(Opcode.LOAD, memAddr, 2))
        machineCodes.append(createInstr(Opcode.CMP, 0, 0))
        machineCodes.append(createInstr(Opcode.JE, 2, 3))
        machineCodes.append(createInstr(Opcode.JMP, -8, 3))
    else:
        machineCodes += loadValue(form.args[0], symbols)
        machineCodes.append(createInstr(Opcode.PRINT, '', 0))
    return machineCodes


def lispScan(form: LispList, symbols):
    assert len(form.args) == 1
    for a in form.args:
        assert a.type == AtomType.CHAR
        if a.type == AtomType.SYMB and symbols[a.content][0] == AtomType.UNDEF:
            assert False

    machineOp = []
    memAddr = symbols[form.args[0].content][2]
    machineOp.append(createInstr(Opcode.SCAN, memAddr, 1))
    return machineOp


def execCmp(form: LispList, jmpSz: int, symbols):
    machineCodes = []
    if isinstance(form, LispAtom):
        if form.content == 'NIL':
            machineCodes.append(createInstr(Opcode.JMP, jmpSz, 3))
        return machineCodes

    assert len(form.args) == 2
  
    left, right = form.args
    if left.type == AtomType.CHAR:
        memAddr = symbols[left.content][2]
        machineCodes.append(createInstr(Opcode.LOAD, memAddr, 1))
    elif left.type == AtomType.PREV:
        machineCodes.append(createInstr(Opcode.LOAD, left.content, 1))
    else:
        machineCodes.append(createInstr(Opcode.LOAD, left.content, 0))

    if right.type == AtomType.CHAR:
        memAddr = symbols[right.content][2]
        machineCodes.append(createInstr(Opcode.CMP, memAddr, 1))
    elif right.type == AtomType.PREV:
        machineCodes.append(createInstr(Opcode.CMP, right.content, 1))
    else:
        machineCodes.append(createInstr(Opcode.CMP, right.content, 0))

    if form.content == '=':
        machineCodes.append(createInstr(Opcode.JNE, jmpSz, 3))
    elif form.content == '!=':
        machineCodes.append(createInstr(Opcode.JE, jmpSz, 3))
    elif form.content == '>=':
        machineCodes.append(createInstr(Opcode.JL, jmpSz, 3))
    elif form.content == '>':
        machineCodes.append(createInstr(Opcode.JLE, jmpSz, 3))
    return machineCodes


def lispIf(form: LispList, condCodes: list, prev: int, symbols):
    machineCodes = []
    machineCodes += condCodes
    cond, thenForm = form.args

    thenCodes = []
    e = evaluate(thenForm, thenCodes, prev, symbols)
    thenCodes = e[0]
    thenCodes += storePrev(prev, symbols)
    symbols = e[2]
    machineCodes += execCmp(cond, len(thenCodes) + 1, symbols)
    machineCodes += thenCodes

    return machineCodes


def lispLoop(machineCodes: list):
    retPos = 0
    machineCodes.append(createInstr(Opcode.JMP, -len(machineCodes), 3))
    for i, instr in enumerate(machineCodes):
        if instr["opcode"] == "hlt" and instr["arg"] == "return":
            retPos = i
    jmpSz = len(machineCodes) - retPos
    machineCodes[retPos] = createInstr(Opcode.JMP, jmpSz, 3)
    return machineCodes


def execFunc(form: LispList, prev: int, symbols):
    machineCodes = []

    if form.content in funcs:
        match form.content:
            case '+' | '-' | '*' | '/' | 'mod' | 'rem':
                machineCodes = lispArith(form, symbols)
                if prev > -1:
                    machineCodes += storePrev(prev, symbols)
            case 'set':
                machineCodes, symbols = lispSetq(form, symbols)
            case 'print':
                machineCodes = lispPrint(form, symbols)
            case 'scan':
                machineCodes = lispScan(form, symbols)
            case 'return':
                machineCodes.append(createInstr(Opcode.HLT, "return", 0))

    return machineCodes, symbols


# [evaluator]
def evaluate(form: LispObject, machineCodes: list, prev, symbols):
    global prevId
    if isinstance(form, LispAtom):
        machineCodes = loadValue(form, symbols)
        return machineCodes, prev, symbols
    args = form.args
    if form.content == 'if':
        cond, formThen = args
        if not isinstance(cond, LispList):
            if cond.type == AtomType.CONST and cond.content == 'NIL':
                pass
            else:
                cond = constT
        # if not isinstance(formThen, LispList):
        #     raise InvalidFunctionSignatureException('then form should be lispLis')

        condCodes = []
        if isinstance(cond, LispList):
            for i, arg in enumerate(cond.args):
                if isinstance(arg, LispList):
                    prevId += 1
                    e = evaluate(arg, condCodes, prevId, symbols)
                    condCodes = e[0]
                    prevLabel = e[1]
                    symbols = e[2]
                    cond.args[i] = LispAtom(prevLabel, AtomType.PREV)

        machineCodes += lispIf(LispList('if', ListType.SPEC, [cond, formThen]), condCodes, prev, symbols)
    elif form.content == 'progn':
        for i, arg in enumerate(args):
            e = evaluate(arg, machineCodes, prev, symbols)
            machineCodes = e[0]
            symbols = e[2]
        machineCodes += storePrev(prev, symbols)
    elif form.content == 'loop':
        for i, arg in enumerate(args):
            e = evaluate(arg, machineCodes, prev, symbols)
            machineCodes = e[0]
            symbols = e[2]
        machineCodes = lispLoop(machineCodes)
    else:
        for i, arg in enumerate(args):
            if isinstance(arg, LispList):
                prevId += 1
                e = evaluate(arg, machineCodes, prevId, symbols)
                machineCodes = e[0]
                prevLabel = e[1]
                symbols = e[2]
                form.args[i] = LispAtom(prevLabel, AtomType.PREV)
        mcodes, symbols = execFunc(form, prev, symbols)
        machineCodes += mcodes
    return machineCodes, prev, symbols
