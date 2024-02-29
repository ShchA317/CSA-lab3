import sys
from ast_classes import *
from isa import Opcode 
from reader import funcs

print(sys.version_info)

buffer = 0
prevId = 0
read_pointer = 101
write_pointer = 102
strPointer = 999


def create_instr(op: Opcode, arg, ismem):
    return {
        "opcode": op,
        "arg": arg,
        "mem": ismem
    }


def load_value(value: LispAtom, symbols) -> list:
    machine_codes = []
    if value.type == AtomType.CHAR:
        address = symbols[value.content][2]
        machine_codes.append(create_instr(Opcode.LOAD, address, 1))
        return machine_codes
    if value.type == AtomType.CONST:
        if value.content == 'T':
            loading_value = 1
        else:
            loading_value = 0
    elif value.type == AtomType.PREV:
        address = int(value.content)
        machine_codes.append(create_instr(Opcode.LOAD, address, 1))
        return machine_codes
    elif value.type == AtomType.STRING:
        loading_value = ord(value.content)
    else:
        loading_value = value.content

    machine_codes.append(create_instr(Opcode.LOAD, loading_value, 0))
    return machine_codes


def store_value(value: LispAtom, symbols) -> list:
    machine_codes = []
    if value.type == AtomType.CHAR:
        address = symbols[value.content][2]
        machine_codes.append(create_instr(Opcode.STORE, address, 1))
        return machine_codes
    if value.type == AtomType.NUM:
        machine_codes.append(create_instr(Opcode.STORE, value.content, 1))
    elif value.type == AtomType.PREV:
        machine_codes.append(create_instr(Opcode.STORE, value.content, 1))
    return machine_codes


def store_string(value: LispAtom, symbols) -> list:
    assert value.type == AtomType.STRING
    machine_codes = []
    global strPointer
    value.content += '\0'
    for ch in reversed(value.content):
        machine_codes += load_value(LispAtom(ch, AtomType.STRING), symbols)
        machine_codes += store_value(LispAtom(strPointer, AtomType.NUM), symbols)
        strPointer -= 1
    return machine_codes


def store_prev(prev, symbols):
    return store_value(LispAtom(prev, AtomType.PREV), symbols)


def lisp_setq(form, symbols):
    machine_op = []
    assert len(form.args) == 2
    assert form.args[0].type == AtomType.CHAR
        
    if form.args[0].content in symbols:
        mem_addr = symbols[form.args[0].content][2]
        symbols[form.args[0].content] = (AtomType.CONST, constNIL, mem_addr)
    if form.args[1].type == AtomType.STRING:
        mem_addr = symbols[form.args[0].content][2]
        symbols[form.args[0].content] = (AtomType.STRING, '', mem_addr)
    else:
        mem_addr = symbols[form.args[0].content][2]
        symbols[form.args[0].content] = (AtomType.CONST, constNIL, mem_addr)

    val = form.args[1]
    t = val.type

    if t == AtomType.STRING:
        machine_op = store_string(val, symbols)
        machine_op += load_value(LispAtom(strPointer + 1, AtomType.NUM), symbols)
        machine_op += store_value(form.args[0], symbols)
        return machine_op, symbols

    if t == AtomType.CHAR:
        assert val.content in symbols
    for i in load_value(form.args[1], symbols):
        machine_op.append(i)
    for i in store_value(form.args[0], symbols):
        machine_op.append(i)
    return machine_op, symbols


def arith_check(form: LispList, symbols) -> bool:
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
    if not arith_check(form, symbols):
        return []

    machine_codes = []

    for instr in load_value(form.args[0], symbols):
        machine_codes.append(instr)

    code = Opcode.ADD
    if form.content == 'rem':
        code = Opcode.REM
    elif form.content == 'mod':
        code = Opcode.MOD
    elif form.content == '-':
        code = Opcode.SUB
    if form.args[1].type == AtomType.PREV:
        machine_codes.append(create_instr(code, int(form.args[1].content), 1))
    elif form.args[1].type == AtomType.CHAR:
        machine_codes.append(create_instr(code, symbols[form.args[1].content][2], 1))
    else:
        machine_codes.append(create_instr(code, form.args[1].content, 0))
    return machine_codes


def lispPrint(form: LispList, symbols):
    assert len(form.args) == 1
    for a in form.args:
        print(a.content)
        if a.type == AtomType.CHAR and symbols[a.content][0] == AtomType.UNDEF:
          assert False
        assert isinstance(a, LispAtom)
        assert a.type in (AtomType.CHAR, AtomType.NUM, AtomType.PREV)
            
        if a.type == AtomType.CHAR and not (symbols[a.content][0] == AtomType.STRING
                                            or symbols[a.content] == 'NIL'
                                            or symbols[a.content] == constNIL
                                            or symbols[a.content][0] == AtomType.CONST
                                            or symbols[a.content][0] == AtomType.NUM):
          assert False

    machine_codes = []
    if form.args[0].type == AtomType.CHAR and symbols[form.args[0].content][0] == AtomType.STRING:
        mem_addr = symbols[form.args[0].content][2]
        machine_codes.append(create_instr(Opcode.LOAD, mem_addr, 2))
        machine_codes.append(create_instr(Opcode.STORE, write_pointer, 1))

        machine_codes.append(create_instr(Opcode.LOAD, mem_addr, 1))
        machine_codes.append(create_instr(Opcode.ADD, 1, 0))
        machine_codes.append(create_instr(Opcode.STORE, mem_addr, 1))

        machine_codes.append(create_instr(Opcode.LOAD, mem_addr, 2))
        machine_codes.append(create_instr(Opcode.CMP, 0, 0))
        machine_codes.append(create_instr(Opcode.JE, 2, 3))
        machine_codes.append(create_instr(Opcode.JMP, -8, 3))
    else:
        machine_codes += load_value(form.args[0], symbols)
        machine_codes.append(create_instr(Opcode.STORE, write_pointer, 1))
    return machine_codes


def lisp_scan(form: LispList, symbols):
    assert len(form.args) == 1
    for a in form.args:
        assert a.type == AtomType.CHAR
        if a.type == AtomType.CHAR and symbols[a.content][0] == AtomType.UNDEF:
            assert False

    machine_op = []
    mem_addr = symbols[form.args[0].content][2]
    machine_op.append(create_instr(Opcode.LOAD, read_pointer, 1))
    return machine_op


def exec_cmp(form: LispList, jmp_sz: int, symbols):
    machine_codes = []
    if isinstance(form, LispAtom):
        if form.content == 'NIL':
            machine_codes.append(create_instr(Opcode.JMP, jmp_sz, 3))
        return machine_codes

    assert len(form.args) == 2
  
    left, right = form.args
    if left.type == AtomType.CHAR:
        mem_addr = symbols[left.content][2]
        machine_codes.append(create_instr(Opcode.LOAD, mem_addr, 1))
    elif left.type == AtomType.PREV:
        machine_codes.append(create_instr(Opcode.LOAD, left.content, 1))
    else:
        machine_codes.append(create_instr(Opcode.LOAD, left.content, 0))

    if form.content == '=':
        machine_codes.append(create_instr(Opcode.JNE, jmp_sz, 3))
    elif form.content == '!=':
        machine_codes.append(create_instr(Opcode.JE, jmp_sz, 3))
    elif form.content == '>=':
        machine_codes.append(create_instr(Opcode.JL, jmp_sz, 3))
    elif form.content == '>':
        machine_codes.append(create_instr(Opcode.JLE, jmp_sz, 3))
    return machine_codes


def lisp_if(form: LispList, condCodes: list, prev: int, symbols):
    machine_codes = []
    machine_codes += condCodes
    cond, then_form = form.args

    then_codes = []
    e = evaluate(then_form, then_codes, prev, symbols)
    then_codes = e[0]
    then_codes += store_prev(prev, symbols)
    symbols = e[2]
    machine_codes += exec_cmp(cond, len(then_codes) + 1, symbols)
    machine_codes += then_codes

    return machine_codes


def lisp_loop(machine_codes: list):
    ret_pos = 0
    machine_codes.append(create_instr(Opcode.JMP, -len(machine_codes), 3))
    for i, instr in enumerate(machine_codes):
        if instr["opcode"] == "hlt" and instr["arg"] == "return":
            ret_pos = i
    jmp_sz = len(machine_codes) - ret_pos
    machine_codes[ret_pos] = create_instr(Opcode.JMP, jmp_sz, 3)
    return machine_codes


def exec_func(form: LispList, prev: int, symbols):
    machine_codes = []

    if form.content in funcs:
        match form.content:
            case '+' | '-' | '*' | '/' | 'mod' | 'rem':
                machine_codes = lispArith(form, symbols)
                if prev > -1:
                    machine_codes += store_prev(prev, symbols)
            case 'set':
                machine_codes, symbols = lisp_setq(form, symbols)
            case 'print':
                machine_codes = lispPrint(form, symbols)
            case 'scan':
                machine_codes = lisp_scan(form, symbols)
            case 'return':
                machine_codes.append(create_instr(Opcode.HLT, "return", 0))

    return machine_codes, symbols


def evaluate(form: LispObject, machine_codes: list, prev, symbols):
    global prevId
    if isinstance(form, LispAtom):
        machine_codes = load_value(form, symbols)
        return machine_codes, prev, symbols
    args = form.args
    if form.content == 'if':
        cond, form_then = args
        if not isinstance(cond, LispList):
            if cond.type == AtomType.CONST and cond.content == 'NIL':
                pass
            else:
                cond = constT

        cond_codes = []
        if isinstance(cond, LispList):
            for i, arg in enumerate(cond.args):
                if isinstance(arg, LispList):
                    prevId += 1
                    e = evaluate(arg, cond_codes, prevId, symbols)
                    cond_codes = e[0]
                    prev_label = e[1]
                    symbols = e[2]
                    cond.args[i] = LispAtom(prev_label, AtomType.PREV)

        machine_codes += lisp_if(LispList('if', ListType.SPEC, [cond, form_then]), cond_codes, prev, symbols)
    elif form.content == 'progn':
        for i, arg in enumerate(args):
            e = evaluate(arg, machine_codes, prev, symbols)
            machine_codes = e[0]
            symbols = e[2]
        machine_codes += store_prev(prev, symbols)
    elif form.content == 'loop':
        for i, arg in enumerate(args):
            e = evaluate(arg, machine_codes, prev, symbols)
            machine_codes = e[0]
            symbols = e[2]
        machine_codes = lisp_loop(machine_codes)
    else:
        for i, arg in enumerate(args):
            if isinstance(arg, LispList):
                prevId += 1
                e = evaluate(arg, machine_codes, prevId, symbols)
                machine_codes = e[0]
                prev_label = e[1]
                symbols = e[2]
                form.args[i] = LispAtom(prev_label, AtomType.PREV)
        mcodes, symbols = exec_func(form, prev, symbols)
        machine_codes += mcodes
    return machine_codes, prev, symbols
