import heart_rate as hr
import heart_rate_helpers as helper
from sys import argv
from logging import debug


def main():
    """
    This is the main file that runs the whole program

    :param str binary_file: name of input binary file
    :param int time: duration of time (in sec) being read-in from binary file
    :param int n: number of signals being multiplexed
    """

    # READ IN COMMNAD LINE ARGUMENTS
    main_args = hr.parse_command_line_args()

    input_file = main_args.input_file
    name = main_args.name
    read_time = main_args.read_time
    age = main_args.age
    N = main_args.N  # number of signals being multiplexed
    N_used = main_args.n_sig_used  # number of signals being used to get HR
    log_level = main_args.log_level

    # NOTE. Initialize the output (logging) file before anything else
    hr.init_output_file(hr.Output_filename, name, log_level)

    # NOTE. Input file type needs to be verified
    file_type = hr.check_input_data(input_file)

    multiplexed_data = hr.multiplex_data(input_file, file_type, N)

    b = 0  # counter for the byte number that is being read in

    # 1. Determine Sampling Frequency, Fs
    Fs, b = hr.read_data(multiplexed_data, b, file_type)
    debug("The sampling frequency is %d Hz.\n" % Fs)

    # 2. Start reading in data based on input time variable
    # A) Make sure time is at least 5 seconds and a whole number
    if read_time < 5:
        read_time = 5
    read_time //= 1

    # B) Calculate amount of samples to take
    samples = helper.myRound(Fs * read_time + 1)

    # C) Initialize list based on input n variable and samples
    signals = [[0 for x in range(samples)] for x in range(N)]
    signals_buffer = [[0 for x in range(samples)] for x in range(N)]

    # D) Read in data
    for i in range(samples):
        for j in range(len(signals)):

            v, b = hr.read_data(multiplexed_data, b, file_type)
            if v == hr.EOF:  # check for EOF
                print(hr.EOF)
                return
            signals[j][i] = v
            signals_buffer[j][i] = v

    # E) Check for NaNs
    for k in range(len(signals)):
        signals[k] = hr.no_NaNsense(signals[k])

    # 3. Estimate Heart Rate
    # A) Remove DC offset
    for l in range(len(signals)):
        signals[l] = hr.remove_offset(signals[l])

    # B) Band Stop Filter
    for m in range(len(signals)):
        signals[m] = hr.band_stop_filter(signals[m], Fs)

    # C) Normalize Data
    for n in range(len(signals)):
        signals[n] = hr.normalize(signals[n])

    # D) Count Peaks
    peaks = [0 for x in range(N)]
    for o in range(len(peaks)):
        peaks[o] = hr.find_peaks(signals[o], Fs)

    # E) Make an Estimation
    heart_rates = [0 for x in range(N)]
    for p in range(len(heart_rates)):
        heart_rates[p] = hr.calculate_heart_rate(peaks[p], read_time)

    HR = hr.calc_hr_with_n_sig(heart_rates, N_used)

    # 4. Processing of Heart Rate
    # A) Test for Bradychardia and Tachycardia
    Bradycardia = hr.detect_bradycardia(HR)
    Tachycardia = hr.detect_tachycardia(HR, age)

    # 5. Output
    # A) Print instantaneous heart rate
    hr.write_inst_to_file(hr.Output_filename, time, HR)

    # B) Check if 1 or 5 minute update should be printed
    one_sum = HR
    five_sum = HR
    start_time1, one_sum = hr.one_minute_update(time, time, one_sum)
    start_time5, five_sum = hr.five_minute_update(time, time, five_sum)

    # C) Write bradycardia/tachycardia warnings to output file
    hr.write_flag_to_file(hr.Output_filename, Bradycardia, Tachycardia)

    # Repeat 2(D) to 5(B) making sure to update next 2 seconds worth of data
    # until EOF reached
    t_cycle = 2
    loop_count = 1
    while True:
        for q in range(len(signals_buffer)):
            signals_buffer[q] = hr.shift_signal_buff(signals_buffer[q], Fs,
                                                     t_cycle)
        signals = signals_buffer

        # 2D) Read in data
        for i in range(samples - (t_cycle * Fs), samples):
            for j in range(len(signals)):

                v, b = hr.read_data(multiplexed_data, b, file_type)
                if v == hr.EOF:  # check for EOF
                    print(hr.EOF)
                    return
                signals[j][i] = v
                signals_buffer[j][i] = v

        # 2E) Check for NaNs
        for k in range(len(signals)):
            signals[k] = hr.no_NaNsense(signals[k])

        # 3. Estimate Heart Rate
        # A) Remove DC offset
        for l in range(len(signals)):
            signals[l] = hr.remove_offset(signals[l])

        # B) Band Stop Filter
        for m in range(len(signals)):
            signals[m] = hr.band_stop_filter(signals[m], Fs)

        # C) Normalize Data
        for n in range(len(signals)):
            signals[n] = hr.normalize(signals[n])

        # D) Count Peaks
        for o in range(len(peaks)):
            peaks[o] = hr.find_peaks(signals[o], Fs)

        # E) Make an Estimation
        for p in range(len(heart_rates)):
            heart_rates[p] = hr.calculate_heart_rate(peaks[p], read_time)

        HR = hr.calc_hr_with_n_sig(heart_rates, N_used)

        # 4. Processing of Heart Rate
        # A) Test for Bradychardia and Tachycardia
        Bradycardia = hr.detect_bradycardia(HR)
        Tachycardia = hr.detect_tachycardia(HR, age)

        # 5. Output
        # A) Print instantaneous heart rate
        hr.write_inst_to_file(hr.Output_filename, time, HR)

        # B) Check if 1 or 5 minute update should be printed
        one_sum += HR
        five_sum += HR
        time, one_sum = hr.one_minute_update(time, time,
                                                    one_sum / loop_count)
        time, five_sum = hr.five_minute_update(time, time,
                                                      five_sum / loop_count)

        # C) Write bradycardia/tachycardia warnings to output file
        hr.write_flag_to_file(hr.Output_filename, Bradycardia, Tachycardia)

        loop_count += 1

if __name__ == '__main__':
    main()
