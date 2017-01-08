    .globl function
    .type function, @function
    .code32
function:
    pushl %edi
    pushl %esi
    movl $0, %edx
    popl %ebx
    popl %eax
    idivl %ebx
    pushl %edx
    popl %eax
    ret