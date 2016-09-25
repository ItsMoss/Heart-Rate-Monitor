import heart_rate as hr

def main(binary_file="test.bin",time=5, n=2):
    """
    This is the main file that runs the whole program
    
    :param str binary_file: name of input binary file
    :param int time: duration of time (in seconds) being read-in from binary file
    :param int n: number of signals being multiplexed
    """    
    
    b = 0 # counter for the byte number that is being read in
    
    # 1. Determine Sampling Frequency, Fs
    Fs, b = hr.read_data(binary_file, b)
    
    # 2. Start reading in data based on input time variable
    # A) Make sure time is at least 5 seconds and a whole number
    if time < 5:
        time = 5
    time //= 1
    
    # B) Calculate amount of samples to take
    samples = Fs * time
    
    # C) Initialize list based on input n variable and samples
    signals = [[0 for x in range(samples)] for x in range(n)]
    
    # D) Read in data
    for i in range(samples):
        for j in range(len(signals)):

            v, b = hr.read_data(binary_file, b)
            if v == hr.EOF: # check for EOF
                print(hr.EOF)
                return
            signals[j][i] = v
            
    # E) Check for NaNs    
    for k in range(len(signals)):
        signals[k] = hr.no_NaNsense(signals[k])
        
    # 3. Estimate Heart Rate
    # A) Remove DC offset and LPF together
    

    # B) Normalize Data


    # C) Count Peaks


    # D) Make an Estimation


    # 4. Processing of Heart Rate
    # A) Test for Bradychardia and Tachycardia


    # 5. Output
    # A) Check if 1 or 5 minute update should be printed

        
    # B) Write to heart_rate_output.txt
        
    
    return # NOTE. Not here yet
    # Repeat 2(D) to 5(B) making sure to update next 2 seconds worth of data
    # until EOF reached
    while True:
        pass

if __name__ == '__main__':
    main()