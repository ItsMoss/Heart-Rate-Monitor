import unittest
import heart_rate as hr

class run(unittest.TestCase):
    
    def test_read_data(self):
        """
        Tests the read_data function from heart_rate.py
        """
        # CREATE BINARY FILE HERE
        binary_file = "test.bin"
        
        v, b = hr.read_data(binary_file, 0)
        
        # DELETE BINARY FILE HERE
        
        self.assertEqual(v, 18, msg="There are 10 types of people...those who know binary and those who do not!")
        self.assertEqual(b, 2, msg="You hungry? Cause these bytes do not add up :P")
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
        
        # Test Case 3 - Two NaNs
        test_list_3 = [1,'NaN',True,3,4]
        output3 = hr.no_NaNsense(test_list_3)
        
        self.assertListEqual(output3, [1,3,3,3,4], msg="You can't make Naan without NaN and you missed two!")
        
        # Test Case 4 - NaNs at both ends
        test_list_4 = ['NaN',1,2,3,True]
        output4 = hr.no_NaNsense(test_list_4)
        
        self.assertListEqual(output4, [1,1,2,3,3], msg="This is driving me baNaNas, maybe I should just compare apples to apples :)")

if __name__ == '__main__':
    unittest.main()