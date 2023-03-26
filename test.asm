.pos 0
irmovq stack, rsp
call main
.pos 20
main:
    irmovq 0xdeadbeef, rax
    halt

.pos 40
stack: