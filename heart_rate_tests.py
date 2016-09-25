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
        
        v, b = hr.read_data(binary_file, 0)
        
        # DELETE BINARY FILE HERE
        
        # Test Case 1 - Accurate output values
        self.assertEqual(v, 1, msg="There are 10 types of people...those who know binary and those who do not!")
        self.assertEqual(b, 1, msg="You hungry? Cause these bytes do not add up :P")
        
        # Test Case 2 - Correct output type
        self.assertEqual(type(b), int, msg="NaN...and I don't mean that delicious Indian bread")
        
    def test_no_NaNsense(self):
        """
        Tests the no_NaNsense function from heart_rate.py
        """
        # Test Case 1 - No NaNs
        test_list_1 = [1,2,3,4,5]
        output1 = hr.no_NaNsense(test_list_1)
        
        self.assertListEqual(output1, test_list_1, msg="If you cannot handle this, we have serious serious problems.")
        
        # Test Case 2 - One NaN
        test_list_2 = [1,2,'NaN',3,5]
        output2 = hr.no_NaNsense(test_list_2)
        
        self.assertListEqual(output2, [1,2,3,3,5], msg="You missed a NaN, double check your receipt maybe.")
        
        # Test Case 3 - Two adjacent NaNs
        test_list_3 = [1,'NaN',True,3,4]
        output3 = hr.no_NaNsense(test_list_3)
        
        self.assertListEqual(output3, [1,0,2,3,4], msg="You can't make Naan without NaN and you missed two!")
        
        # Test Case 4 - Two non-adjacent NaNs
        test_list_4 = [1,'NaN',3,True,6]
        output4 = hr.no_NaNsense(test_list_4)
        
        self.assertListEqual(output4, [1,2,3,5,6], msg="You can't make Naan without NaN even if they are spaced out!")
        
        # Test Case 5 - NaNs at both ends
        test_list_5 = ['NaN',1,2,3,True]
        output5 = hr.no_NaNsense(test_list_5)
        
        self.assertListEqual(output5, [1,1,2,3,3], msg="This is driving me baNaNas, maybe I should just compare apples to apples :)")
        
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
        

if __name__ == '__main__':
    unittest.main()