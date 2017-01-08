#Error types so that we could be more specific.
class ParseError(ValueError):
    pass

class TokenError(ValueError):
    pass

def tokenize(code):
    """Gives out a list of tokens, token by token.
       The types are integers, operators, and parenthesis."""
    num_st = -1
    for i in range(len(code)):
        #the token is a single character...
        if code[i] in ['(', ')', '+', '-', '*']:
            if num_st != -1:
                #if we were preparing a multi-char int, spit it out.
                yield (code[num_st: i])
                num_st = -1
            yield (code[i])
        elif code[i].isdigit():
            #start preparing a number
            if num_st == -1:
                num_st = i
        elif code[i].isspace():
            #if there's whitespace, a token has ended.
            #whitespace itself is not a token.
            if num_st != -1:
                yield (code[num_st: i])
                num_st = -1
        else:
            #if a token is something else, raise an error.
            raise TokenError("Unidentified token: " + code[i])

    if num_st != -1:
        #if the code ends in a number, spit that token out.
        yield code[num_st:]

def parse(toks, fn_name = "function", tabs = ' ' * 4):
    #the prelude.
    lines = [tabs + '.globl ' + fn_name,
             tabs + '.type ' + fn_name + ', @function',
             tabs + '.code32',
             fn_name + ':']
    #code to prepare each operation
    ops = {'*': [tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'imull %ebx, %eax', tabs + 'pushl %eax'],
           '+': [tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'addl %ebx, %eax', tabs + 'pushl %eax'],
           '-': [tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'subl %ebx, %eax', tabs + 'pushl %eax']}

    #the innards function is passed to allow for mutual recursion.
    #s_expr may call innards and innards may call s_expr.
    #this circular dependency is resolved by the arguments innards_fn and s_expr_fn.
    def s_expr(innards_fn):
        nonlocal lines
        curr = next(toks)
        if curr == '(':
            #A paren means innards.
            innards_fn(s_expr)
            #A paren must be matched.
            if next(toks) != ')':
                raise ParseError("Mismatched parenthesis or non-binary use of operator")
        elif curr.isdigit():#digits mean a constant value.
            lines.append(tabs + 'pushl $' + curr)
        else: #we don't know what token came here...
            raise ParseError("Unexpected token: " + curr)

    def innards(s_expr_fn):
        nonlocal lines
        op = next(toks)
        #expect an operator
        if op not in ops:
            raise ParseError("Undefined operator: " + op)
        #handle the arguments.
        s_expr_fn(innards)
        s_expr_fn(innards)
        #Add the operator's code.
        lines += ops[op]

    try:
        s_expr(innards)
        return '\n'.join(lines + [tabs + 'popl %eax', tabs + 'ret'])
    except StopIteration:
        raise ParseError("Unexpected end of file.")

def compile(infile, fn_name = "function", tabs = ' ' * 4, outfile = 'a'):
    #this is useful in the header...
    include_test_macro = '_'.join([fn_name, outfile, 'incl', 'test'])
    with open(infile) as fl:
        try:
            asm = parse(tokenize(fl.read()), fn_name = fn_name, tabs = tabs)
        except Exception as e:
            print("Error:", e.args[0])
            print("No output generated!")
            return
        with open(outfile + '.s', 'w') as ofs: #write the assembly
            ofs.write(asm)
        with open(outfile + '.h', 'w') as ofh: #write the header
            ofh.write("#ifndef " + include_test_macro + "\n#define " + include_test_macro + "\nint " + fn_name + "();\n#endif")

if __name__ == "__main__":
    from sys import argv, exit
    args = argv[1:] #the command-line arguments
    if len(args) == 0 or args[0] == '-h':
        print("USAGE: " + argv[0] + " 'input file' -fn='function name' -tabs='indentation for assembly file' -out='output file name'")
        print("-h will print this message.")
        print("All the other arguments with a dash (after the file name) can appear in any order.")
        print("The function name is expected to be a valid C function name.")
        print("The output file name is used to start the name for a '.s' with the assembly and a '.h' to include in C.")
    else:
        infile = args[0]
        fn_name = "function"
        tabs = ' '*4
        outfile = 'a'
        opts = {'-fn', '-tabs', '-out'}
        for i in args[1:]:
            opt, val = i.split('=', 1)
            if opt not in opts:
                print("Unrecognized argument :" + i)
                print("Use '" + argv[0] + " -h' for the help message")
                exit(1)
            elif opt == '-fn':
                fn_name = val
            elif opt == '-tabs':
                tabs = val
            else:
                outfile = val

        compile(infile, fn_name, tabs, outfile)

