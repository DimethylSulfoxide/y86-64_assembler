# irmovq      0xf, rax, 1
# irmovq      0xf, rcx, 101
# irmovq      0xf, rdx, 0
# irmovq      0xf, rbx, 1
# irmovq      0xf, rsp, 101
# irmovq      0xf, r9, 0
# loop:
# rrmovq      rsp, rcx
# addq         rax, rdx
# addq         rbx, rax
# subq         rax, rcx
# jl          loop
# rmmovq      rdx, r9, 88

irmovq 0xf, rax, 0x12344321