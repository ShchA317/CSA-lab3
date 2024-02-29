from reader import lispMyASTBuilder

print(lispMyASTBuilder('(+ 1 2 3)')[0][0].args[2])

print(lispMyASTBuilder('(+ (+ 1 2) (+ 1 2) 1 (+ 1 2 3)) (- 10 1)')[0][0].args[3].args[1])

print(lispMyASTBuilder('(print "hello")'))