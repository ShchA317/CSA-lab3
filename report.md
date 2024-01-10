# Лабораторная работа №3. Отчет
- P33151, Щербаков Александр Валерьевич
- lisp | acc | harv | hw | instr | struct | stream | mem | pstr | prob5 | [4]char

## Язык программирования

Lisp-подобный. S-expressions. Любое выражение -- expression

BNF: 
```
program       ::= statement*
statement     ::= expression | assignment | control_structure

expression    ::= '(' operator operand* ')'
operator      ::= + | - | * | :

assignment    ::= '(' 'set' symbol expression ')'

control_structure ::= '(' if_statement | for_loop | defun_statement ')'

if_statement     ::= 'if' expression statement (else_statement)?
else_statement  ::= 'else' statement

for_loop      ::= '(' 'for' symbol '(' start end ')' expression* ')'

defun_statement      ::= '(' 'defun' symbol '(' symbol* ')' expression* ')'

operand       ::= expression | symbol | literal_value
symbol        ::= any valid symbol name
start, end    ::= any valid integer value
literal_value ::= number | string | boolean
string ::= '"' [a-z A-Z 1-9 \s]+ '"'
```

## Организация памяти

### Память команд
Реализуется списком словарей, описывающих инструкции (одно слово -- одна ячейка).

### Память данных 

- Линейное адресное пространство. Адресуется числами от 0 до n
- Одна ячейка - 64 бит.

память разделена на 6 блоков, размеры блоков, а также их расположение относительно друг друга конфигурируется.

Например, по-умолчанию используется конфигурация, где адреса 
- 0 - 299     определены под   переменные и константы
- 300 - 599   определены под   строки
- 600 - 849   определены под   промежуточные итоги выполнения
- 850         определен под    буфер ввода
- 851         оперделен под    буфер вывода
- 900 - 2047  определены под   стек данных

## Система команд

#### режимы адресации
- в адресные команды “зашит” актуальный режим адрессации \
у операндов поддерживаются следующие режимы адресации:

| Режим | Описание |
| ----- | ---- |
| CONSTANT | операнд хранится непосредственно в команде |
| DIRECT_ADDRESS | операнд - это значение, лежащее по адресу, хранящемся в команде |

### Набор инструкций

| команда | режимы адрессации | описание |
| --- | --- | --- |
| add | CONSTANT, DIRECT_ADDRESS | AC + operand |
| mul | CONSTANT, DIRECT_ADDRESS | AC * operand |
| div | CONSTANT, DIRECT_ADDRESS | AC / operand |
| mod | CONSTANT, DIRECT_ADDRESS | AC % operand |
| cmp | CONSTANT, DIRECT_ADDRESS |  |
| jmp | CONSTANT |  |
| je | CONSTANT |  |
| call | CONSTANT |  |
| ret | - |  |
| ld | CONSTANT, DIRECT_ADDRESS |  |
| st | CONSTANT |  |
| hlt | - |  |
| push | - |  |
| pop | - |  |


### Кодирование инструкций

- Машинный код сериализуется в список JSON.
- Один элемент списка -- одна инструкция.
- Индекс списка -- адрес инструкции. Используется для команд перехода.

  
Пример:
```json
[
    {
        "opcode": "jmp",
        "arg": 1,
        "mode": "constant"
    },
    {
        "opcode": "ld",
        "arg": 1,
        "mode": "direct_address"
    },
    {
        "opcode": "hlt"
    }
]
```

где:

opcode -- строка с кодом операции;
arg -- аргумент (может отсутствовать);
mode -- режим адресации (может отсутствовать)

