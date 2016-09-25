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
            signal[i] = helper.myAverage(low, hi)
        
    # Lastly, let's check the first and last indices
    if type(signal[0]) != int:
        signal[0] = signal[1]
    if type(signal[-1]) != int:
        signal[-1] = signal[-2]
    
    signal_no_nan = signal
    
    return signal_no_nan
    
def remove_offset(signal):
    """
    This function removes DC offset of an input signal
    
    :param list signal: input signal
    :return list signal_clean: cleaned up signal (i.e. without offset)
    """
    from numpy import int16, ones, convolve
    
    np_signal = helper.list2numpy(signal)
    
    window = len(signal) // 5
    avg_signal = convolve(np_signal, ones(window, dtype=int16) / window, mode='same')
    signal_clean = np_signal - avg_signal
    
    signal_clean = helper.numpy2list(signal_clean)
    
    return signal_clean
    
def band_stop_filter(signal, Fs, Fc=60):
    """
    This function filters out frequencies close to a desired cutoff Fc (in Hz).
    The default Fc is 60 Hz as that is most common for unwanted noise
    
    :param list signal: input signal
    :param int Fs: sampling frequency in Hz
    :param int Fc: cutoff frequency in Hz
    :return list signal_clean: cleaned up signal (i.e. filtered)
    """
    from scipy.signal import butter, filtfilt
    
    np_signal = helper.list2numpy(signal)
    
    # Create filter
    nyq_f = Fs / 2
    f_range = 2
    f_low = (Fc - f_range) / nyq_f
    f_hi = (Fc + f_range) / nyq_f
    
    b, a = butter(3, [f_low, f_hi], 'bandstop')
    
    # Apply filter
    pad = len(signal) // 10
    filt_signal = filtfilt(b, a, np_signal, padlen=pad)

    signal_clean = helper.numpy2list(filt_signal)
    
    return signal_clean
    
def normalize(signal):
    """
    This function normalizes all values from -1 to 1
    
    :param list signal: input signal
    :return list norm_signal: normalized signal
    """
    # Let's find the maximum and minimum values
    maximum = max(signal)
    minimum = min(signal)
    
    # Choose the one with greater magnitude
    greatest = abs(maximum)
    if abs(maximum) < abs(minimum):
        greatest = abs(minimum)
        
    # Normalize
    for i, v in enumerate(signal):
        signal[i] = round(v / greatest, 2)
        
    norm_signal = signal
    
    return norm_signal

def find_peaks(signal, Fs):
    """
    This function finds all local maxima within a given signal
    
    :param list signal: inut signal
    :return int peak_count: number of peaks detected
    """
    
    # First create a simple kernel resembling a QRS complex
    QRSkernel = makeQRSkernel(Fs)
    
    # Cross-correlate QRS kernel with signal
    sigXkern = cross_correlate(signal, QRSkernel)
    
    # Count up peaks
    peak_count = 0
    threshold = 0.6 * max(sigXkern)
    for x in sigXkern:
        if x >= threshold:
            peak_count += 1
    
    return peak_count
    