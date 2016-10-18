import unittest
import heart_rate as hr
import heart_rate_helpers as helper


class run(unittest.TestCase):

    def test_read_data(self):
        """
        Tests the read_data function from heart_rate.py
        """
        # CREATE BINARY FILE HERE
        binary_file = "test.bin"

        v1, b1 = hr.read_data(binary_file, 0)
        v2, b2 = hr.read_data(binary_file, b1)

        # DELETE BINARY FILE HERE

        # Test Case 1 - Accurate output values
        self.assertEqual(v1, 1, msg="There are 10 types of people...those who know binary and those who do not!")
        self.assertEqual(v2, 4, msg="there are 2 types of people...those who do not know anything but decimal and others!")
        self.assertEqual(b1, 2, msg="You hungry? Cause these bytes do not add up :P")
        self.assertEqual(b2, 4, msg="The number four (4) is a beautiful number")

        # Test Case 2 - Correct output type
        self.assertEqual(type(v1), int, msg="NaN...and I don't mean that delicious Indian bread")

    def test_no_NaNsense(self):
        """
        Tests the no_NaNsense function from heart_rate.py
        """
        # Test Case 1 - No NaNs
        test_list_1 = [1, 2, 3, 4, 5]
        output1 = hr.no_NaNsense(test_list_1)

        self.assertListEqual(output1, test_list_1, msg="If you cannot handle this, we have serious serious problems.")

        # Test Case 2 - One NaN
        test_list_2 = [1, 2, 'NaN', 3, 5]
        output2 = hr.no_NaNsense(test_list_2)

        self.assertListEqual(output2, [1, 2, 3, 3, 5], msg="You missed a NaN, double check your receipt maybe.")

        # Test Case 3 - Two adjacent NaNs
        test_list_3 = [1, 'NaN', True, 3, 4]
        output3 = hr.no_NaNsense(test_list_3)

        self.assertListEqual(output3, [1, 0, 2, 3, 4], msg="You can't make Naan without NaN and you missed two!")

        # Test Case 4 - Two non-adjacent NaNs
        test_list_4 = [1,'NaN',3,True,6]
        output4 = hr.no_NaNsense(test_list_4)

        self.assertListEqual(output4, [1,2,3,5,6], msg="You can't make Naan without NaN even if they are spaced out!")

        # Test Case 5 - NaNs at both ends
        test_list_5 = ['NaN', 1, 2, 3, True]
        output5 = hr.no_NaNsense(test_list_5)

        self.assertListEqual(output5, [1, 1, 2, 3, 3], msg="This is driving me baNaNas, maybe I should just compare apples to apples :)")


    def test_remove_offset(self):
        """
        Tests the remove_offset function from heart_rate.py
        """
        from random import randrange

        # Test Case 1 - Only DC
        test_list_1 = [10 for x in range(20)]
        output1 = hr.remove_offset(test_list_1)

        self.assertAlmostEqual(helper.listAverage(output1[2:-2]), 0, msg="Unable to handle DC? must not be a fan of Batman I presume.")

        # Test Case 2 - Randomly Generated signal        
        test_list_2 = [randrange(20) for x in range(20)]
        output2 = hr.remove_offset(test_list_2)

        self.assertLessEqual(helper.listAverage(output2), helper.listAverage(test_list_2), msg="Averaging of signal is more screwed up than...a screw")

        # Test Case 3 - Periodic Square wave
        test_list_3 = [0 for x in range(5)] + [10 for x in range(5)]
        test_list_3 = test_list_3 + test_list_3
        output3 = hr.remove_offset(test_list_3)

        self.assertEqual(max(output3), 5, msg="Don't be square, be aware...of your mistakes")


    def test_band_stop_filter(self):
        """
        Tests the band_stop_filter function from heart_rate.py
        """
        t = 20
        A = 2
        Fs = 500

        # Test Case 1 - Only DC
        test_list_1 = [A for x in range(t)]
        output1 = hr.band_stop_filter(test_list_1, Fs)

        diff1 = abs(helper.listAverage(output1) - helper.listAverage(test_list_1))
        self.assertLessEqual(diff1, 0.5, msg="Unable to handle DC?...do you have something against Superman?")

        # Test Case 2 - ~60 Hz only
        f62 = 62
        test_list_2 = list(helper.makeSine(t, A, f62))
        output2 = hr.band_stop_filter(test_list_2, Fs)

        self.assertLessEqual(abs(helper.listAverage(output2)), 0.5, msg="You are not even stopping what you claim to be stopping...")

        # Test Case 3 - 20 Hz only
        f20 = 20
        test_list_3 = list(helper.makeSine(t, A, f20))
        output3 = hr.band_stop_filter(test_list_3, Fs)

        diff3 = abs(helper.listAverage(output3) - helper.listAverage(test_list_3))
        self.assertLessEqual(diff3, 0.5, msg="This frequency should not be stopped, it should be go'ed")


    def test_normalize(self):
        """
        Tests the normalize function from heart_rate.py
        """
        from random import randrange

        # Test Case 1 - Random Signal 1
        test_list_1 = [randrange(-20, 20) for x in range(20)]
        output1 = hr.normalize(test_list_1)

        self.assertLessEqual(max(output1), 1, msg="I think you accidentally used your abnormalize function")
        self.assertGreaterEqual(min(output1), -1, msg="You should probably just delete the abnormalize function")
        if test_list_1[0] == 0:
            self.assertEqual(output1[0], 0, msg="Values that are zero should stay zero")
        elif test_list_1[0] > 0:
            self.assertGreaterEqual(output1[0], 0, msg="Positive values should remain positive")
        elif test_list_1[0] < 0:
            self.assertLessEqual(output1[0], 0, msg="Negative values should remain negative")

        # Test Case 2 - Random Signal 2
        test_list_2 = [randrange(-20, 20) for x in range(20)]
        output2 = hr.normalize(test_list_2)

        self.assertLessEqual(max(output2), 1, msg="I think your abnormalize function was inadvertently used")
        self.assertGreaterEqual(min(output2), -1, msg="Something seems unusally abnormal, for something that should be normal...")
        if test_list_2[0] == 0:
            self.assertEqual(output2[0], 0, msg="Zero normalied should still be zero")
        elif test_list_2[0] > 0:
            self.assertGreaterEqual(output2[0], 0, msg="I am positive that you messed up the positive values")
        elif test_list_2[0] < 0:
            self.assertLessEqual(output2[0], 0, msg="Not trying to be negative, but you definitely messed this up")


    def test_make_QRS_kernel(self):
        """
        Tests the make_QRS_kernel function from heart_rate.py
        """
        # Test Case 1 - 50 samples/sec
        Fs1 = 50
        output1 = hr.make_QRS_kernel(Fs1)

        self.assertListEqual(output1, [0, 0.33, 0.67, 1, 0.50, 0], msg="50 Hz kernel does not even look like a triangle")

        # Test Case 2 - 20 samples/sec
        Fs2 = 20
        output2 = hr.make_QRS_kernel(Fs2)

        self.assertListEqual(output2, [0, 1, 0], msg="This 20 Hz kernel looks worse than molded popcorn")


    def test_cross_correlate(self):
        """
        Tests the cross_correlate function from heart_rate.py
        """
        from random import randrange
        kernel = [0, 0.5, 1, 0.5, 0]

        # Test Case 1 - Random Signal 1
        test_list_1 = [randrange(20) for x in range(10)]
        output1 = hr.cross_correlate(test_list_1, kernel)
        test_var1a = 0.5 * (test_list_1[1] + test_list_1[3]) + test_list_1[2]
        test_var1b = 0.5 * (test_list_1[6] + test_list_1[8]) + test_list_1[7]

        self.assertEqual(len(output1), 6, msg="Output of cross correlation is incorrect length. Need a ruler?")
        self.assertEqual(output1[0], test_var1a, msg="You are doing something wrong at the start of cross correlation")
        self.assertEqual(output1[-1], test_var1b, msg="You are doing something wrong at the end of cross correlation")

        # Test Case 2 - Random Signal 2
        test_list_2 = [randrange(20) for x in range(12)]
        output2 = hr.cross_correlate(test_list_2, kernel)
        test_var2a = 0.5 * (test_list_2[1] + test_list_2[3]) + test_list_2[2]
        test_var2b = 0.5 * (test_list_2[8] + test_list_2[10]) + test_list_2[9]

        self.assertEqual(len(output2), 8, msg="Wait, were you using metric or imperial units...or both?")
        self.assertEqual(output2[0], test_var2a, msg="Something at the start of your cross-correlation is way off the mark...palmeri")
        self.assertEqual(output2[-1], test_var2b, msg="Something at the end of your cross correlation is way off the mark...cuban")


    def test_find_peaks(self):
        """
        Tests the find_peaks function from heart_rate.py
        """
        from numpy import pi

        t = 4 * pi
        A = 1
        f = 1 / (2 * pi)

        Fs = 700

        # Test Case 1 - Signal with 2 obvious peaks
        test_list_1 = list(helper.makeSine(t, A, f))
        output1 = hr.find_peaks(test_list_1, Fs)

        self.assertEqual(output1, 2, msg="If you cannot count peaks, you really need to re-think career paths")

        # Test Case 2 - Signal with 3 peaks (but 2 are the first and last value respectively)
        test_list_2 = list(helper.makeCosine(t, A, f))
        output2 = hr.find_peaks(test_list_2, Fs)

        self.assertEqual(output2, 3, msg="Don't forget to check the ends, they have feelings too")

        # Test Case 3 - Only DC (i.e. no peaks)
        test_list_3 = [A for x in range(helper.myRound(t))]
        output3 = hr.find_peaks(test_list_3, Fs)

        self.assertEqual(output3, 0, msg="Did you know that you don't need to count, to count zero times?")


    def test_calculate_heart_rate(self):
        """
        Tests the calculate_heart_rate function from heart_rate.py
        """
        beats1 = 8
        beats2 = 4
        beats3 = 14
        time1 = 5
        time2 = 9
        time3 = 2
        
        # Test Case 1 - 8 beats
        self.assertEqual(hr.calculate_heart_rate(beats1, time1), 96, msg="Learn how to divide 8 / 5 then multiply 60")
        self.assertEqual(hr.calculate_heart_rate(beats1, time2), 53.33, msg="Learn how to divide 8 / 9 then multiply 60")
        self.assertEqual(hr.calculate_heart_rate(beats1, time3), 240, msg="Learn how to divide 8 / 2 then multiply 60")
        
        # Test Case 2 - 4 beats
        self.assertEqual(hr.calculate_heart_rate(beats2, time1), 48, msg="Learn how to divide 4 / 5 then multiply 60")
        self.assertEqual(hr.calculate_heart_rate(beats2, time2), 26.67, msg="Learn how to divide 4 / 9 then multiply 60")
        self.assertEqual(hr.calculate_heart_rate(beats2, time3), 120, msg="Learn how to divide 4 / 2 then multiply 60")        
        
        # Test Case 3 - 14 beats
        self.assertEqual(hr.calculate_heart_rate(beats3, time1), 168, msg="Learn how to divide 14 / 5 then multiply 60")
        self.assertEqual(hr.calculate_heart_rate(beats3, time2), 93.33, msg="Learn how to divide 14 / 9 then multiply 60")
        self.assertEqual(hr.calculate_heart_rate(beats3, time3), 420, msg="Learn how to divide 14 / 2 then multiply 60")
        
    def test_detect_bradycardia(self):
        """
        Tests the detect_bradycardia function from heart_rate.py
        """
        # Test Case 1 - Has Bradycardia
        hr1 = 20
        output1 = hr.detect_bradycardia(hr1)
        
        self.assertEqual(output1, True, msg="Maybe you are missing a few heartbeats yourself?")
        
        # Test Case 2 - Does NOT
        hr2 = 70
        output2 = hr.detect_bradycardia(hr2)
        
        self.assertEqual(output2, False, msg="Maybe you are NOT missing some heartbeats, but ARE missing some brain cells")
        
    def test_detect_tachycardia(self):
        """
        Tests the detect_tachycardia function from heart_rate.py
        """
        age = 25

        # Test Case 1 - Has Tachycardia
        hr1 = 200
        output1 = hr.detect_tachycardia(hr1, age)

        self.assertEqual(output1, True, msg="Maybe you have a few too many heartbeats yourself?")

        # Test Case 2 - Does NOT
        hr2 = 70
        output2 = hr.detect_tachycardia(hr2, age)

        self.assertEqual(output2, False, msg="Maybe you do NOT a few too many heartbeats, but a few too many [insert insult]")

    def test_time_10s(self):
        """
        Tests ability to time for an alotted amount of time, in this case 10s
        """
        from time import time

        start = time()
        end = time()
        while end - start <= 10:
            end = time()

        elapsed = end - start
        print("Elapsed time: %r" % elapsed)

        self.assertLessEqual(abs(elapsed - 10), 0.05, msg="I know you are not a clock, but you have to do better than that")


if __name__ == '__main__':
    unittest.main()
