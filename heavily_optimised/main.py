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
        if code[i] in ['(', ')', '+', '-', '*', '/', '%', 'L', 'R']:
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
    #or a function to execute an operation.
    ops = {'*': ([tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'imull %ebx, %eax', tabs + 'pushl %eax'], lambda x, y: x * y),
           '+': ([tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'addl %ebx, %eax', tabs + 'pushl %eax'], lambda x, y: x + y),
           '-': ([tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'subl %ebx, %eax', tabs + 'pushl %eax'], lambda x, y: x - y),
           '/': ([tabs + 'popl %eax', tabs + 'popl %ebx', tabs + 'idivl %ebx', tabs + 'pushl %eax'], lambda x, y: x // y),
           '%': ([tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'idivl %ebx', tabs + 'pushl %edx'], lambda x, y: x % y)}

    #the stack depth
    max_depth = 0
    depth = 0

    #handles updating the stack depth.
    def do_push_depth(ch = 1):
        nonlocal depth, max_depth
        depth = depth + ch
        if depth > max_depth:
            max_depth = depth

    #the innards function is passed to allow for mutual recursion.
    #s_expr may call innards and innards may call s_expr.
    #this circular dependency is resolved by the arguments innards_fn and s_expr_fn.
    def s_expr(innards_fn):
        nonlocal lines
        curr = next(toks)
        if curr == '(':
            #A paren means innards.
            v = innards_fn(s_expr)
            #A paren must be matched.
            if next(toks) != ')':
                raise ParseError("Mismatched parenthesis or non-binary use of operator")
            return v
        elif curr.isdigit():#digits mean a constant value.
            return int(curr)
        elif curr == 'L': #the left parameter, not a compile-time constant
            lines.append(tabs + 'pushl %edi')
            do_push_depth()
            return None
        elif curr == 'R': #the right parameter
            lines.append(tabs + 'pushl %esi')
            do_push_depth()
            return None
        else: #we don't know what token came here...
            raise ParseError("Unexpected token: " + curr)

    def innards(s_expr_fn):
        nonlocal lines
        op = next(toks)
        #expect an operator
        if op not in ops:
            raise ParseError("Undefined operator: " + op)
        #handle the arguments.
        l = s_expr_fn(innards)
        r = s_expr_fn(innards)
        #Add the operator's code.
        if l is not None and r is not None:
            #propogate constants by doing the operation itself.
            return ops[op][1](l, r)
        else:
            #otherwise, make sure the values are on the stack
            if l is not None:
                lines.append(tabs + 'pushl $' + str(l))
                do_push_depth()
            if r is not None:
                lines.append(tabs + 'pushl $' + str(r))
                do_push_depth()

            #prepare for a division.
            if op in ['/', '%']:
                lines.append(tabs + 'movl $0, %edx')
            lines += ops[op][0]
            do_push_depth(-1)
            return None

    try:
        v = s_expr(innards)
        if v is not None:
            print("This program has a constant value:", v)
            lines.append(tabs + 'movl $' + str(v) + ', %eax')
            #this minimizes instructions to two.
            #any of the bare_bones implementation will lead to this.
            return '\n'.join(lines + [tabs + 'ret']), 0
        return '\n'.join(lines + [tabs + 'popl %eax', tabs + 'ret']), max_depth
    except StopIteration:
        raise ParseError("Unexpected end of file.")

def compile(infile, fn_name = "function", tabs = ' ' * 4, outfile = 'a'):
    #this is useful in the header...
    include_test_macro = '_'.join([fn_name, outfile, 'incl', 'test'])
    with open(infile) as fl:
        try:
            asm, md = parse(tokenize(fl.read()), fn_name = fn_name, tabs = tabs)
        except Exception as e:
            print("Error:", e.args[0])
            print("No output generated!")
            return
        print("The program pushes " + str(md) + " integers onto the stack, using " + str(md * 4) + " bytes.")
        print("Generating files...")
        with open(outfile + '.s', 'w') as ofs: #write the assembly
            ofs.write(asm)
        with open(outfile + '.h', 'w') as ofh: #write the header
            ofh.write("#ifndef " + include_test_macro + "\n#define " + include_test_macro + "\nint " + fn_name + "(int L, int R);\n#endif")

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

