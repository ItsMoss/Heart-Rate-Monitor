import heart_rate_helpers as helper

EOF = "\nEnd Of File reached!\n"
Bradycardia_detected = "\nWarning: Signs of bradycardia detected! Refer to hea\
rt_rate_output.txt for details.\n"
Tachycardia_detected = "\nWarning: Signs of tachycardia detected! Refer to hea\
rt_rate_output.txt for details.\n"
Output_filename = "heart_rate_output"


def parse_command_line_args():
    """
    This function parses command line arguments and returns them

    :return object args: contains all parsed command line arguments
    """
    import argparse as argp

    parser = argp.ArgumentParser(description="Command line argument parser for\
    heart_rate_main.py")

    parser.add_argument("--input_file",
                        dest="input_file",
                        help="Input file. Only binary, MATLAB formatted data, \
                        and HDF5 are supported. DEFAULT=data16bit.bin",
                        type=str,
                        default="data16bit.bin")
    parser.add_argument("--user_name",
                        dest="name",
                        help="Full name of the user. DEFAULT=Assignment 03",
                        type=str,
                        default="Assignment 03")
    parser.add_argument("--user_age",
                        dest="age",
                        help="Age of the user. DEFAULT=25",
                        type=int,
                        default=25)
    parser.add_argument("--read_time",
                        dest="read_time",
                        help="Amount of time in seconds to calculate heart rat\
                        e on. DEFAULT=5 (note, 5 is the minimum allowed)",
                        type=int,
                        default=5)
    parser.add_argument("--N_multiplex",
                        dest="N",
                        help="Amount of signals being multiplexed in binary fi\
                        le. DEFAULT=2",
                        type=int,
                        default=2)
    parser.add_argument("--N_used",
                        dest="n_sig_used",
                        help="The signal being used to estimate heart rate, st\
                        arting from 0. If greater than or equal to N_multiplex\
                        all signals are used. DEFAULT=2",
                        type=int,
                        default=2)
    parser.add_argument("--log_level",
                        dest="log_level",
                        help="Level of logging user wishes to be printed to ou\
                        tput file. Accepatable values are DEBUG, INFO, WARNING\
                        , ERROR, and CRITICAL. DEFAULT=DEBUG",
                        type=str,
                        default="DEBUG")

    args = parser.parse_args()

    # Let's check for some errors real quick
    # 1. N_multiplex cannot be less than 1
    if args.N < 1:
        print("Command line argument error! N_multiplex cannot be less than 1.\
        \n")
        raise ValueError
    # 2. N_used cannot be less than 0...and if it is greater than N_multiplex
    if args.n_sig_used < 0:
        print("Command line argument error! N_used cannot be less than 0.\n")
        raise ValueError
    elif args.n_sig_used > args.N:
        args.n_sig_used = args.N

    return args


def check_input_data(input_file):
    """
    This function determines what the input file type is: It accommodates
    binary, HDF5, and MATLAB formatted data files.

    :param str input_file: name of the input file
    :return str ftype: the determined file type of input_file
    """
    import logging as log

    log.debug("Determining input data file type.\n")

    try:
        # 1. Testing for MATLAB formatted data file
        from scipy.io import loadmat

        f = loadmat(input_file)
        ftype = ".mat"
    except ValueError:
        try:
            # 2. Testing for HDF5 file
            from h5py import File

            f = File(input_file, 'r')
            f.close()
            ftype = ".hdf5"
        except OSError:
            # 3. Assume a binary file
            ftype = ".bin"

    return ftype


def multiplex_data(input_file, ftype, n_mp):
    """
    This file multiplexes the input data for .mat and .hdf5 files

    :param str input_file: name of input file
    :param str ftype: input file type
    :param int n_mp: number of signals being multiplexed
    :return mpx_data: the multiplexed data (this remains a file if ftype is th\
    at of a binary file, therefore making returning a str...otherwise a list\
    is returned
    """
    if ftype == ".bin":
        return input_file

    import logging as log

    log.debug("Multiplexing input data.\n")

    if n_mp != 2:
        log.error("You did not specify the required number of signals to be mu\
        ltiplexed=2.")
        raise IndexError

    if ftype == ".mat":
        from scipy.io import loadmat

        f = loadmat(input_file)
        Fs = f.get("Fs")[0][0]
        ECG = list(f.get("ECG")[0])
        PP = list(f.get("PP")[0])

    elif ftype == ".hdf5":
        from h5py import File

        f = File(input_file, 'r')
        Fs = f.get("Fs").shape[0]
        ECG = list(f.get("ECG").shape)
        PP = list(f.get("PP").shape)
        f.close()

    else:
        log.error("Unexpected input file format.\n")
        raise IOError

    mpx_data = helper.multiplex(Fs, ECG, PP)

    return mpx_data


def read_data(multplx_data, read_from, dtype):
    """
    This function reads in a single byte from a binary file and converts it to
    integer value assuming bit size of 16

    :param multplx_data: name of the input binary file (str) OR list of data \
    from either an input MATLAB formatted data or HDF5 file
    :param int read_from: represents the number byte to start reading from
    :param str dtype: input file type (should be one of the returned values\
    from 'check_input_data')
    :return int v: the integer value of the byte read
    :return int read_from: represents the next byte number to be read
    """
    import logging as log
    log.debug("Reading in data.\n")

    if dtype == ".bin":
        with open(multplx_data, 'rb') as f:
            f.seek(read_from)
            bs = f.read(2)
            if bs == b'':
                return EOF, read_from
            try:
                v = int.from_bytes(bs, 'little')
            except TypeError:
                v = None

        read_from += 2

    else:
        try:
            v = int(multplx_data[read_from])
            read_from += 1
        except ValueError:
            log.error("Unexpected data type in input file.\n")
            raise ValueError
        except IndexError:
            return EOF, read_from

    return v, read_from


def no_NaNsense(signal):
    """
    This function makes sure that all values within the input list are integers
    If a NaN occurs linear interpolation is attempted, and if that fails the
    value is set to 0

    :param list signal: a list
    :return list signal_no_nan: list without any NaN's
    """
    import logging as log
    log.debug("Removing NaNs from signal.\n")

    # Firstly, let's check that the length of the list is greater than 2
    if len(signal) < 3:
        errormsg = "This list representing your signal is too small. Length=%d\
        \n" % len(signal)
        log.error(errormsg)
        print(errormsg)
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
    import logging as log
    log.debug("Removing DC offset.\n")

    from numpy import int16, ones, convolve

    np_signal = helper.list2numpy(signal)

    window = len(signal) // 5
    avg_signal = convolve(np_signal, ones(window, dtype=int16)/window,
                          mode='same')
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
    import logging as log
    log.debug("Applying band stop filter.\n")

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
    import logging as log
    log.debug("Normalizing signal.\n")

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


def make_QRS_kernel(Fs, amplitude=1):
    """
    This function creates a kernel resembling a QRS complex based on input
    sampling frequency Fs. This function assumes the average QRS complex
    time-length of 0.10 seconds, and simply creates a spike at 0.05 seconds
    with linear slope on each side going to zero (i.e. a triangular wave).

    :param int Fs: sampling frequency in Hz
    :param int amplitude: amplitude of spike
    :return list kernel: calculated QRS kernel
    """
    import logging as log
    log.debug("Creating transient QRS kernel.\n")

    # Initialize list based off of Fs
    t = 0.10   # QRS time-length
    samples = helper.myRound(Fs * t + 1)

    if samples < 3:
        errormsg = "\nSampling frequency is ridiculously low\n"
        print(errormsg)
        log.error(errormsg)
        raise IndexError  # This really should not happen

    kernel = [0 for x in range(samples)]

    # Create spike
    spike_at = helper.myRound((samples - 1) / 2)  # index of spike
    slope_up = amplitude / spike_at
    slope_down = -1 * amplitude / (samples - 1 - spike_at)

    for i in range(1, spike_at):
        kernel[i] = round(i * slope_up, 2)

    kernel[spike_at] = amplitude

    for j in range(spike_at + 1, samples - 1):
        kernel[j] = round((j - spike_at) * slope_down + amplitude, 2)

    return kernel


def cross_correlate(signal, kernel):
    """
    This function cross correlates a signal with a kernel, where the kernel
    has time-length less than the signal and is slid across the signal

    :param list signal: input signal
    :param list kernel: input kernel
    :return list x_coeffs: list of calculated cross correlation coefficients
    """
    import logging as log
    log.debug("Cross correlating signal and kernel.\n")

    if len(kernel) >= len(signal):
        errormsg = "\nKernel length cannot be greater than signal length\n"
        print(errormsg)
        log.error(errormsg)
        raise IndexError

    # Initialize correlation coefficients list
    return_length = len(signal) - len(kernel) + 1
    x_coeffs = [0 for x in range(return_length)]

    k_len = len(kernel)

    for i in range(return_length):
        overlap = signal[i:i+k_len]
        x_coeffs[i] = helper.dotProduct(overlap, kernel)

    return x_coeffs


def find_peaks(signal, Fs):
    """
    This function finds all local maxima within a given signal

    :param list signal: inut signal
    :return int peak_count: number of peaks detected
    """
    import logging as log
    log.debug("Finding peaks in signal.\n")

    L = len(signal)
    threshold = 0.6 * max(signal)
    peak_count = 0
    above = False

    # Make sure peaks actually even exist, otherwise return 0
    dc = signal[0]
    i = 0
    while dc == signal[i]:
        i += 1
        if i == len(signal) - 1:
            return 0

    # Look for changes from above to below the threshold
    for j in range(L - 1):
        if signal[j] > threshold:
            above = True
        else:
            above = False
        if above is True and signal[j+1] <= threshold:
            peak_count += 1

    # Check last value
    if signal[-1] > threshold and above is True:
        peak_count += 1

    return peak_count


def calculate_heart_rate(beats, time):
    """
    This function calculates heart rate (in bpm)

    :param int beats: number of detected beats
    :param int time: number of elapsed seconds
    :return float hr: calculated heart rate in bpm
    """
    import logging as log
    log.debug("Calculating heart rate.\n")

    hr = beats / time * 60

    return round(hr, 2)


def detect_bradycardia(heart_rate):
    """
    This function makes best guess as to whether bradycardia is being exhibited

    :param float heart_rate: heart rate in bpm
    :return ble bradycardia: whether or not bradycardia detected
    """
    import logging as log
    log.debug("Checking for bradycardia.\n")

    hr_low = 50  # Assuming a heart rate below 50 bpm is too slow

    bradycardia = False
    if heart_rate < hr_low:
        bradycardia = True

    return bradycardia


def detect_tachycardia(heart_rate, age):
    """
    This function makes best guess as to whether tachycardia is being exhibited

    :param float heart_rate: heart rate in bpm
    :param int age: age of user/patient
    :return ble tachycardia: whether or not tachycardia detected
    """
    import logging as log
    log.debug("Checking for tachycardia.\n")

    hr_hi = round(207 - (0.7 * age), 2)

    tachycardia = False
    if heart_rate > hr_hi:
        tachycardia = True

    return tachycardia


def one_minute_update(timer, avg_summed, counter):
    """
    This function determines if one minute has passed between printing 1 minute
    average heart rate, and prints 1 minute average if one minute has elapsed

    :param float timer: the current time in seconds since last 1 minute span
    :param int avg_summed: summed average heart rates for passed 1 minute
    :param int counter: counter of how many averages have beenn taken past min
    :return float new_timer: new start time(only change if one minute elapsed)
    :return int new_avg: new summed averages count for passed 1 minute
    :return int new_count: new counter, reset if 1 minute elapsed
    """
    import logging as log
    log.debug("Checking if one-minute average should be calculated.\n")

    new_timer = timer
    new_avg = avg_summed
    new_count = counter

    if timer >= 60:
        log.debug("Calculating one-minute average.\n")

        hr = avg_summed / counter

        write_line = "One minute average: heart rate=%.2f bpm\n" % hr

        print(write_line)

        log.info(write_line)

        new_timer = 0
        new_avg = 0
        new_count = -1  # must be -1 because end of while loop in main
        # increments

    return new_timer, new_avg, new_count


def five_minute_update(timer, avg_summed, counter):
    """
    This function determines if five minutes passed between printing 5 minute
    average heart rate, and prints 5 minute average if five minutes has elapsed

    :param float timer: the current time in seconds since last 5 minute span
    :param int avg_summed: summed average heart rates for passed 5 minutes
    :param int counter: counter of how many averages have beenn taken past 5min
    :return float new_timer: new start time(only change if five minute elapsed)
    :return int new_avg: new summed averages count for passed 5 minutes
    :return int new_count: new counter, reset if 5 minutes elapsed
    """
    import logging as log
    log.debug("Checking if five-minute average should be calculated.\n")

    new_timer = timer
    new_avg = avg_summed
    new_count = counter

    if timer >= 300:
        log.debug("Calculating five-minute average.\n")

        hr = avg_summed / counter

        write_line = "Five minute average: heart rate=%.2f bpm\n" % hr

        print(write_line)

        log.info(write_line)

        new_timer = 0
        new_avg = 0
        new_count = 0  # must be -1 because end of while loop in main
        # increments

    return new_timer, new_avg, new_count


def init_output_file(fname, name, log_level):
    """
    This function initializes an output file for continuous log of heart rate
    data for a user/patient (in .txt format)

    :param str fname: desired name for output file (without file extension)
    :param str name: name of the user/patient
    :param str log_level: the desired level of logging for the output file
    """
    import logging as log

    log.basicConfig(filename=fname+'.log', level=helper.logDict[log_level])
    message = "This file is a continuous Heart Rate log for "+name+"\n"
    log.info(message)

    return


def write_inst_to_file(filename, time, hr):
    """
    This function writes instantaneous heart rate to output file and also
    prints same informtion to terminal

    :param str filename: output file name
    :param float time: current time in seconds
    :param float hr: calculated instantaneous heart rate in bpm
    """
    import logging as log
    write_line = "time=%.2f s   |   heart rate=%.2f bpm\n" % (time, hr)

    print(write_line)

    log.info(write_line)

    return


def write_min_to_file(filename, hr, minutes='one'):
    """
    This function writes one and five minute averages to output file and also
    prints same information to terminal

    :param str filename: output file name
    :param float hr: calculated average heart rate
    :param str minutes: minutes for which average is being printed for
    """
    if minutes == 'one' or minutes == 'five':
        import logging as log
        write_line = "\n"+minutes+"-minute average=%.2f bpm\n" % (hr)

        print(write_line)

        log.info(write_line)

    return


def write_flag_to_file(filename, bradycardia, tachycardia):
    """
    This function writes flag to output file for if bradycardia or tachycardia
    was detected and prints corresponding information to terminal

    :param str filename: output file name
    :param ble bradycardia: whether or not bradycardia detected
    :param ble tachycardia: whether or not tachycardia detected
    """

    if bradycardia is True:
        import logging as log
        log.warning(Bradycardia_detected)

        print(Bradycardia_detected)

    if tachycardia is True:
        import logging as log
        log.warning(Tachycardia_detected)

        print(Tachycardia_detected)

    return


def shift_signal_buff(signal, Fs, t=2):
    """
    This function shifts the signal buffer list by the amount of samples
    corresponding to time t

    :param list signal: the signal buffer
    :param int Fs: sampling frequency in Hz
    :param int t: time to shift by in seconds
    :return list new_signals: updated signals buffer
    """
    import logging as log
    log.debug("Manipulating the signal buffer.\n")

    remove_buffer = Fs * t + 1
    pad = [0 for x in range(remove_buffer + 1)]

    new_signal = signal[remove_buffer:-1] + pad

    return new_signal


def calc_hr_with_n_sig(heart_rates, n):
    """
    This function determines the heart rate using a user-specified amount of
    signals

    :param list heart_rates: list of the calculated heart rates for all signals
    :param int n: the signal number that one wants to use to calculate HR (bpm)
    :return float hr: calculated HR (in bpm)
    """
    import logging as log
    log.debug("Calculating heart rate.\n")

    N = len(heart_rates)

    if n == N:
        hr = helper.listAverage(heart_rates)
    else:
        try:
            hr = heart_rates[n]
        except IndexError:
            errormsg = "An error occurred trying to use signal #%d to calculat\
            e heart rate!" % n
            log.error(errormsg)
            print(errormsg)
            hr = helper.listAverage(heart_rates)

    return round(hr, 2)
