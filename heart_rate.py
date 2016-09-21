def main():
    """
    This is the main file that runs the whole program
    """
    b = 0
    t = 1
    n = 2
    
    Fs, b = read_data("test.bin", b)
    samples = Fs * t
    
    signals = [[0 for x in range(samples)] for x in range(n)]
    
    for i in range(samples):
        for j in range(len(signals)):
            v, b = read_data("test.bin", b)
            signals[j][i] = v
        
            print("signal %d: " %(j+1), signals[j])

def read_data(file, read_from):
    """
    This function reads in a binary file and converts it to integer values
    assuming bit size of 16
    
    :param str file: name of the input binary file
    :param int read_from: represents the number byte to start reading from
    """
    with open(file, 'rb') as f:
        f.seek(read_from)
        bs = f.read(1)
        v = int.from_bytes(bs, 'little')
        
    return v, read_from + 2

if __name__ == '__main__':
    main()