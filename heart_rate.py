import heart_rate_helpers as helper

EOF = "\nEnd Of File reached!\n"
Bradycardia_detected = "\nWarning: Signs of bradycardia detected! Refer to heart_rate_output.txt for details.\n"
Tachycardia_detected = "\nWarning: Signs of tachycardia detected! Refer to heart_rate_output.txt for details.\n"
Output_filename = "heart_rate_output"


def parse_command_line_args():
    """
    This function parses command line arguments and returns them

    :return object args: contains all parsed command line arguments
    """
    import argparse as argp

    parser = argp.ArgumentParser(description = "Command line argument parser for heart_rate_main.py")

    parser.add_argument("--binary_file",
                        dest="binary_file",
                        help="Input binary file",
                        type=str,
                        default="test.bin")
    parser.add_argument("--user_name",
                        dest="name",
                        help="Full name of the user",
                        type=str,
                        default="Assignment 02")
    parser.add_argument("--user_age",
                        dest="age",
                        help="Age of the user",
                        type=int,
                        default=25)
    parser.add_argument("--read_time",
                        dest="read_time",
                        help="Amount of time in seconds to calculate heart rate on",
                        type=int,
                        default=5)
    parser.add_argument("--N_multiplex",
                        dest="N",
                        help="Amount of signals being multiplexed in binary file",
                        type=int,
                        default=2)
    parser.add_argument("--N_used",
                        dest="n_sig_used",
                        help="The signal being used to estimate heart rate, starting from 0. If greater than or equal to N_multiplex all signals are used.",
                        type=int,
                        default=2)

    args = parser.parse_args()

    # Let's check for some errors real quick
    # 1. N_multiplex cannot be less than 1
    if args.N < 1:
        print("Command line argument error! N_multiplex cannot be less than 1.\n")
        raise ValueError
    # 2. N_used cannot be less than 0...and if it is greater than N_multiplex
    if args.n_sig_used < 0:
        print("Command line argument error! N_used cannot be less than 0.\n")
        raise ValueError
    elif args.n_sig_used > args.N:
    	args.n_sig_used = args.N

    return args


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

    return v, read_from + 2


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
    # Initialize list based off of Fs
    t = 0.10   # QRS time-length
    samples = helper.myRound(Fs * t + 1)

    if samples < 3:
        print("\nSampling frequency is ridiculously low\n")
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
    if len(kernel) >= len(signal):
        print("\nKernel length cannot be greater than signal length\n")
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

    hr = beats / time * 60

    return round(hr, 2)


def detect_bradycardia(heart_rate):
    """
    This function makes best guess as to whether bradycardia is being exhibited

    :param float heart_rate: heart rate in bpm
    :return ble bradycardia: whether or not bradycardia detected
    """

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

    hr_hi = round(207 - (0.7 * age), 2)

    tachycardia = False
    if heart_rate > hr_hi:
        tachycardia = True

    return tachycardia


def one_minute_update(current_time, start_time, avg_hr):
    """
    This function determines if one minute has passed between printing 1 minute
    average heart rate, and prints 1 minute average if one minute has elapsed

    :param float current_time: the current time in seconds of program running
    :param float start_time: time in seconds of program start
    :param int avg_hr: total beats count for passed minute
    :return float new_start: new start time (only change if one minute elapsed)
    """
    new_start = start_time

    if current_time - start_time > 60:
        # print one minute average
        new_start = current_time
        return new_start

    return new_start


def five_minute_update(current_time, start_time, avg_hr):
    """
    This function determines if five minutes passed between printing 5 minute
    average heart rate, and prints 5 minute average if five minutes has elapsed

    :param float current_time: the current time in seconds of program running
    :param float start_time: time in seconds of program start
    :param int avg_hr: total beats count for passed 5 minutes
    :return float new_start: new start time(only change if five minute elapsed)
    """
    new_start = start_time

    if current_time - start_time > 300:
        # print five minute average
        new_start = current_time
        return new_start

    return new_start


def init_output_file(filename, name):
    """
    This function initializes an output file for continuous log of heart rate
    data for a user/patient (in .txt format)

    :param str filename: desired name for output file (without file extension)
    :param str name: name of the user/patient
    """

    with open(filename+".txt", 'w') as f:
        f.write("This file is a continuous Heart Rate log for "+name+"\n\n")


def write_inst_to_file(filename, time, hr):
    """
    This function writes instantaneous heart rate to output file and also
    prints same informtion to terminal

    :param str filename: output file name
    :param float time: current time in seconds
    :param float hr: calculated instantaneous heart rate in bpm
    """
    write_line = "time=%.2f s   |   heart rate=%.2f bpm\n" % (time, hr)

    print(write_line)

    with open(filename+".txt", 'a') as f:
        f.write(write_line)

    
def write_min_to_file(filename, hr, minutes='one'):
    """
    This function writes one and five minute averages to output file and also
    prints same information to terminal

    :param str filename: output file name
    :param float hr: calculated average heart rate
    :param str minutes: minutes for which average is being printed for
    """
    if minutes == 'one' or minutes == 'five':
        write_line = "\n"+minutes+"-minute average=%.2f bpm\n" % (hr)

        print(write_line)

        with open(filename+".txt", 'a') as f:
            f.write(write_line)


def write_flag_to_file(filename, bradycardia, tachycardia):
    """
    This function writes flag to output file for if bradycardia or tachycardia
    was detected and prints corresponding information to terminal

    :param str filename: output file name
    :param ble bradycardia: whether or not bradycardia detected
    :param ble tachycardia: whether or not tachycardia detected
    """

    if bradycardia is True:
        with open(filename+".txt", 'a') as f:
            f.write(Bradycardia_detected)

        print(Bradycardia_detected)

    if tachycardia is True:
        with open(filename+".txt", 'a') as f:
            f.write(Tachycardia_detected)

        print(Tachycardia_detected)


def shift_signal_buff(signals, Fs, t=2):
    """
    This function shifts the signal buffer list by the amount of samples
    corresponding to time t

    :param list signals: the signals buffer
    :param int Fs: sampling frequency in Hz
    :param int t: time to shift by in seconds
    :return list new_signals: updated signals buffer
    """
    remove_buffer = Fs * t
    pad = [0 for x in range(remove_buffer)]

    new_signals = signals[remove_buffer:-1] + pad

    return new_signals


def calc_hr_with_n_sig(heart_rates, n):
    """
    This function determines the heart rate using a user-specified amount of
    signals

    :param list heart_rates: list of the calculated heart rates for all signals
    :param int n: the signal number that one wants to use to calculate HR (bpm)
    :return float hr: calculated HR (in bpm)
    """
    N = len(heart_rates)

    if n == N:
        hr = helper.listAverage(heart_rates)
    else:
        try:
            hr = heart_rates[n]
        except IndexError:
            print("An error occurred trying to use signal #%d to calculate heart rate!" % n)
            hr = helper.listAverage(heart_rates)

    return round(hr, 2)
