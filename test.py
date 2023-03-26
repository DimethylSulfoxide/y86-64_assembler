a = input()
match a:
    case '1' | '2' | '3' | '4':
        print('nums')
    case 'a' | 'b' | 'c':
        print('alphabet')
    case _:
        print("unknown option")
