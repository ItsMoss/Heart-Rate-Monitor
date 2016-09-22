def main():
    """
    This is the main file that runs the whole program
    """
    b = 0 # counter for the byte number that is being read in
    t = 1 # time in seconds to take samples from
    n = 2 # number of signals being multiplexed
    binary_file = "" # NOTE. I should go back and make these parameters into main()
    
    Fs, b = read_data(binary_file, b)
    samples = Fs * t
    
    signals = [[0 for x in range(samples)] for x in range(n)]
    
    for i in range(samples):
        for j in range(len(signals)):
            v, b = read_data(binary_file, b)
            signals[j][i] = v
        
            print("signal %d: " %(j+1), signals[j]) # NOTE. This is for testing

def read_data(file, read_from):
    """
    This function reads in a single byte from a binary file and converts it to
    integer value assuming bit size of 16
    
    :param str file: name of the input binary file
    :param int read_from: represents the number byte to start reading from
    :return int v: the integer value of the byte read
    :return int read_from + 2: represents the next byte number to be read
    """
    with open(file, 'rb') as f:
        f.seek(read_from)
        bs = f.read(1)
        v = int.from_bytes(bs, 'little')
        
    return v, read_from + 2
    
def check_data(signals):
    """
    This function ensures that all values read in from the input signal are
    valid (i.e. not NaN) in order to do arithmetic on
    
    :param list signals: contains the read-in signal(s)
    """
    pass

if __name__ == '__main__':
    main()