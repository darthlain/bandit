def lines(name, encoding = 'utf-8'):
    with open(str(name), encoding = encoding) as f:
        return [i[:-1] for i in f.readlines()]

def replaces(name, lst, encoding = 'utf-8'):
    with open(str(name), 'w', newline = '\n', encoding = encoding) as f:
        for i in lst:
            f.write(i + '\n')

def insert(name, s, encoding = 'utf-8'):
    lst = [str(s)]
    lst.extend(lines(name, encoding = encoding))
    replaces(name, lst, encoding = encoding)

def filter(name, fn, encoding = 'utf-8'):
    lst = lines(name, encoding = encoding)
    lst = [i for i in lst if fn(i)]
    replaces(name, lst, encoding = encoding)
