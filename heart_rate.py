import heart_rate_helpers as helper

EOF = "\nEnd Of File reached!\n"

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
        if bs == b'':
            return EOF, read_from
        try:
            v = int.from_bytes(bs, 'little')
        except TypeError:
            v = None
        
    return v, read_from + 1

def no_NaNsense(signal):
    """
    This function makes sure that all values within the input list are integers
    If a NaN occurs linear interpolation is attempted, and if that fails the
    value is set to 0
    
    :param list signal: a list
    :return list signal_no_nan: list without any NaN's
    """
    
    # Firstly, let's check that the length of the list is greater than 2
    if len(signal) < 3:
        print("This list representing your signal is too small. Length=%d\n" % len(signal))
        raise IndexError
    
    # Now let's check all values excluding the first and last indices
    for i, v in enumerate(signal):
        if i == 0 or i == len(signal) - 1:
            continue
        if type(v) != int:
            low = signal[i-1]
            hi = signal[i+1]
            signal[i] = helper.listAverage(low, hi)
        
    # Lastly, let's check the first and last indices
    if type(signal[0]) != int:
        signal[0] = signal[1]
    if type(signal[-1]) != int:
        signal[-1] = signal[-2]
    
    signal_no_nan = signal
    
    return signal_no_nan