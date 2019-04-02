import sys


def format(file):
    with open(file) as f:
        content = f.readlines()
    
    formated = []

    content = [x.strip() for x in content]
    for x in content:
        tmp = x.split(',')
        tmp = [x.strip() for x in tmp]
        tmp = [f'\'{s}\'' if not s.isdigit() else '' for s in tmp]
        tmp.append('?')
        str1 = ",".join(tmp)
        formated.append(str1)
    formated = [f'({s}),' for s in formated]
    for x in formated:
        print(x)

def formatrec(file):
    with open(file) as f:
        content = f.readlines()
    
    formated = []

    content = [x.strip() for x in content]
    for x in content:
        tmp = x.split(',')
        tmp = [x.strip() for x in tmp]
        tmp = [f'\'{s}\'' if not s.isdigit() else s for s in tmp]
        tmp[0],tmp[2] = tmp[2], tmp[0]
        tmp[1],tmp[2] = tmp[2], tmp[1]
        str1 = ",".join(tmp)
        formated.append(str1)
    formated = [f'({s}),' for s in formated]
    for x in formated:
        print(x)

    


if __name__ == "__main__":
    formatrec(sys.argv[1])