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
        

if __name__ == '__main__':
    unittest.main()