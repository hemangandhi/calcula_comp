#Calcula Compiler

This project includes files for compiling "calcula" programs.

##What is calcula?

Calcula is a dummy-language that, with a Scheme-like syntax, denotes basic mathematical operations on integer constants.

`(+ (+ 1 2) 3)` encodes `1 + 2 + 3`.

Subtraction (`-`) and multiplication (`*`) are also supported.

##What the compiler compiles to...

So far only IA32 is supported. The stack is heavily used.

`gcc -O` must be used as the return value is left in the `eax` register.

##Using compiled files.

The compiler produces a `.h` and a `.s`. In a C file, the `.h` can be regularly included. Compilation can be done as follows:
    gcc -O file_in_c.c compiled_file.s
