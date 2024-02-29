from reader import lisp_my_ast_builder

print(lisp_my_ast_builder('(+ 1 2 3)')[0][0].args[2])

print(lisp_my_ast_builder('(+ (+ 1 2) (+ 1 2) 1 (+ 1 2 3)) (- 10 1)')[0][0].args[3].args[1])

print(lisp_my_ast_builder('(print "hello")'))