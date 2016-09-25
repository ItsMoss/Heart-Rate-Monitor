import heart_rate as hr

def main(binary_file="test.bin",time=5, n=2):
    """
    This is the main file that runs the whole program
    
    :param str binary_file: name of input binary file
    :param int time: duration of time (in seconds) being read-in from binary file
    :param int n: number of signals being multiplexed
    """    
    
    b = 0 # counter for the byte number that is being read in
    
    Fs, b = hr.read_data(binary_file, b) # determine sampling frequency
    
    # make sure time is at least 5 seconds and a whole number
    if time < 5:
        time = 5
    time //= 1
    
    samples = Fs * time
    
    signals = [[0 for x in range(samples)] for x in range(n)]
    
    for i in range(samples):
        for j in range(len(signals)):

            v, b = hr.read_data(binary_file, b)
            signals[j][i] = v
    
    for k in range(len(signals)):
        signals[k] = hr.no_NaNsense(signals[k])
        
    print("signal 1: %r" % signals[0])
    print("signal 2: %r" % signals[1])

if __name__ == '__main__':
    main()