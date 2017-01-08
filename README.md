#Calcula Compiler

This project includes files for compiling "calcula" programs.

##What is calcula?

Calcula is a dummy-language that, with a Scheme-like syntax, denotes basic mathematical operations on integer constants.

`(+ (+ 1 2) 3)` encodes `1 + 2 + 3`.

Subtraction (`-`) and multiplication (`*`) are also supported.

In the heavily optimized version, modulo (`%`) and division (`/`) are supported as well. Furthermore, L and R can be used for arguments.

##What the compiler compiles to...

So far only IA32 is supported. The stack is heavily used.

`gcc -O` must be used as the return value is left in the `eax` register.

The heavily optimized version evaluates all constants at compile-time, reducing the run time of the code.

##Using compiled files.

The compiler produces a `.h` and a `.s`. In a C file, the `.h` can be regularly included. Compilation can be done as follows:

```bash
gcc -O file_in_c.c compiled_file.s
```
