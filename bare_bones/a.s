    .globl function
    .type function, @function
    .code32
function:
    pushl $2
    pushl $123
    pushl $321
    popl %ebx
    popl %eax
    addl %ebx, %eax
    pushl %eax
    popl %ebx
    popl %eax
    imull %ebx, %eax
    pushl %eax
    pushl $222
    popl %ebx
    popl %eax
    subl %ebx, %eax
    pushl %eax
    popl %eax
    ret
