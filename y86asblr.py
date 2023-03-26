import re

directives = {
    ".pos": "i",
    ".align": "i",
    ".quad": "i",
}

instructions = {
    "halt": ["", "00"],
    "nop": ["", "10"],
    "rrmovq": ["rr", "20"],
    "cmovle": ["rr", "21"],
    "cmovl": ["rr", "22"],
    "cmove": ["rr", "23"],
    "cmovne": ["rr", "24"],
    "cmovge": ["rr", "25"],
    "cmovg": ["rr", "26"],
    "irmovq": ["rri", "30"],
    "rmmovq": ["rri", "40"],
    "mrmovq": ["rri", "50"],
    "addq": ["rr", "60"],
    "subq": ["rr", "61"],
    "andq": ["rr", "62"],
    "xorq": ["rr", "63"],
    "jmp": ["i", "70"],
    "jle": ["i", "71"],
    "jl": ["i", "72"],
    "je": ["i", "73"],
    "jne": ["i", "74"],
    "jge": ["i", "75"],
    "jg": ["i", "76"],
    "call": ["i", "80"],
    "ret": ["", "90"],
    "pushq": ["rr", "a0"],
    "popq": ["rr", "b0"]
}

regs2num = {
    "rax": 0, "rcx": 1, "rdx": 2, "rbx": 3, "rsp": 4, "rbp": 5, "rsi": 6, "rdi": 7,
    "r8": 8, "r9": 9, "r10": 10, "r11": 11, "r12": 12, "r13": 13, "r14": 14, "nil": 15,
}


class sentence():
    start_address = 0
    end_address = 0
    length = 0
    label_name = ''
    instr_name = ''
    r1 = 'nil'
    r2 = 'nil'
    imm = 0x0
    islabel = False

    def __init__(self, start_address: int, length: int, label_name: str = '', instr_name: str = '', r1: str = 'nil', r2: str = 'nil', imm: int = 0x0) -> None:
        self.start_address = start_address
        self.length = length
        self.label_name = label_name
        self.instr_name = instr_name
        self.r1 = r1 if r1 != '0xf' else 'nil'
        self.r2 = r2 if r2 != '0xf' else 'nil'
        self.imm = imm
        self.end_address = start_address + length
        self.islabel = self.label_name and not self.instr_name
        if (self.islabel):
            self.label_name = label_name[:-1]

    def __repr__(self) -> str:
        if self.label_name and not self.instr_name:  # labels
            return "%0.8x\t%s\n" % (self.start_address, self.label_name)
        elif not self.label_name and self.instr_name:  # instructions but not j or call
            return "%0.8x\t%s, %s, %s, %x\n" % (self.start_address, self.instr_name, self.r1, self.r2, self.imm)
        else:  # j or call
            return "%0.8x\t%s, %s\n" % (self.start_address, self.instr_name, self.label_name)


def remove_comments(a: str) -> str:
    return re.sub(r'#.*', '', a)


def remove_symbols(a: str) -> str:
    return re.sub(r'[\(\),$%]', '', a)

def bige2lite(a: int) -> str:
    tmp = "%0.16x" % a
    res = ''
    for i in range(0, 16, 2):
        res += tmp[14 - i: 16 - i]
    return res

def is_str_10or16based_num(a:str)->bool:
    try:
        int(a)
        return True
    except ValueError:
        pass
    try:
        int(a, 16)
        return True
    except ValueError:
        pass
    return False

def pre_process(codes: list) -> list:
    # 只需要特殊处理irmovq和push pop和rm(mr)movq
    res = []
    for line in codes:
        if not line:
            continue
        else:
            # print(line)
            newline = []
            match line[0]:
                case "irmovq":
                    newline = ['irmovq', 'nil', line[-1], line[1]]

                case "pushq" | "popq":
                    newline = line.append('nil')

                case "rmmovq":
                    if len(line) == 4:
                        newline = [line[0], line[1], line[3], line[2]]
                    else :
                        newline = [line[0], line[1], line[2], '0']

                case "mrmovq":
                    if len(line) == 4:
                        newline = [line[0], line[2], line[3], line[1]]
                    else :
                        newline = [line[0], line[1], line[2], '0']
                
                case others:
                    newline = line


            res.extend(newline)
    return res




def get_sentences(codes: list) -> list:
    sentences = []
    i = 0
    while i < len(codes):
        current_address = sentences[-1].end_address if sentences else 0
        if codes[i][-1] == ':':  # label
            sentences.append(sentence(current_address, 0, codes[i]))
        else:  # instructions

            length = 0
            r1 = 'nil'
            r2 = 'nil'
            imm = 0
            instr_name = codes[i]
            label_name = ''

            match instructions[codes[i]][0]:
                case '':
                    length = 1

                case 'rr':
                    length = 2
                    r1 = codes[i+1]
                    r2 = codes[i+2]
                    i += 2

                case 'i':  # j系列和call, 涉及到标签转换为地址
                    length = 9
                    label_name = codes[i+1]
                    i += 1

                case 'rri':  # irmovq同样涉及标签转地址
                    length = 10
                    r1 = codes[i+1]
                    r2 = codes[i+2]
                    if codes[i] == "irmovq" and not is_str_10or16based_num(codes[i+3]):
                        label_name = codes[i+3]
                    else: 
                        if codes[i+3][0:2] == '0x':
                            imm = int(codes[i+3], 16)
                        else:
                            imm = int(codes[i+3])
                    i += 3

            sentences.append(sentence(current_address, length,
                             label_name, instr_name, r1, r2, imm))

        i += 1
    return sentences
    pass


def get_hexcodes(sentences: list) -> list:
    hexcodes = []
    for i in sentences:
        hcode = ''
        if i.islabel:
            continue
        else:
            hcode += instructions[i.instr_name][1]
            match instructions[i.instr_name][0]:
                case '':
                    pass

                case 'rr':
                    hcode += "%0.1x" % (regs2num[i.r1])
                    hcode += "%0.1x" % (regs2num[i.r2])

                case 'i':  # j系列和call, 涉及到标签转换为地址
                    target = 0
                    find = False
                    for j in sentences:
                        if not j.islabel:
                            continue
                        else:
                            if j.label_name == i.label_name:
                                target = j.start_address
                                find = True
                    if not find:
                        print("No such label named %s." % i.label_name)
                    hcode += bige2lite(target)
                    pass

                case 'rri': # irmovq同样可能涉及标签转地址
                    hcode += "%0.1x" % (regs2num[i.r1])
                    hcode += "%0.1x" % (regs2num[i.r2])
                    if i.instr_name == 'irmovq' and i.label_name:
                        target = 0
                        find = False
                        for j in sentences:
                            if not j.islabel:
                                continue
                            else:
                                if j.label_name == i.label_name:
                                    target = j.start_address
                                    find = True
                        if not find:
                            print("No such label named %s." % i.label_name)
                        hcode += bige2lite(target)
                    else:
                        hcode += bige2lite(i.imm)
            pass

        # print(hcode)
        hexcodes.append(hcode)
    return hexcodes


def main():
    filename = input("汇编文件名:")
    f = open(filename, 'r')
    code = remove_comments(f.read())
    code = remove_symbols(code)
    processed_code = pre_process([i.split() for i in code.split('\n')])
    sentences = get_sentences(processed_code)
    hexcodes = get_hexcodes(sentences)
    # print(hexcodes)
    # print(sentences)
    f.close
    of = open(filename.split('.')[0] + ".bin", 'w')
    for i in hexcodes:
        of.write(i + '\n')
    of.close()
    print('已写入%s.'%(filename.split('.')[0] + ".bin"))
    # pre_process(code.split())

    # a = code.split('\n')
    # for i in a:
    #     print(i.split())


if __name__ == '__main__':
    main()
