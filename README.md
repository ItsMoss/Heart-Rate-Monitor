# Assignment 02
By: Moseph Jackson-Atogi

The following documents lists and outlines all files for BME590 Assignemnt02, in which a code for a heart rate monitor was developed in Python 3.5. Directions for how to run the program properly are also included.

+ `heart_rate_main.py` runs the entire program. It uses functions imported from heart_rate_helpers.py and heart_rate.py to execute properly.

+ `heart_rate.py` contains all functions used in heart_rate_main.py for reading an input binary, estimating heart rate, processing heart rate, and outputting calculated data

+ `heart_rate_helpers.py` contains various helper functions called in both heart_rate.py and heart_rate_main.py, but that are not part of the core algorithm in calculating heart rate

+ `heart_rate_tests.py` contains all unit tests for functionality of program (i.e. heart_rate_main.py). Each function, excluding the output functions, in heart_rate.py is tested in this file.

+ `createTest.sh` is a shell script used to create a binary file for testing.

+ `test.bin` is a test binary file created as a result of running createTest.sh shell script

## Instructions for Running Program

To run the code for calculating heart rate properly, follow the below steps:

1. Open `heart_rate_main.py` in your text editor/IDE of preference

2. Replace input parameter **binary_file** with your own binary file

  * This should be on or around line 4 depending on your editor
  
  * Currently, the file name *test.bin* is in that place

3. Optionally, replace input parameters **name** and **age** with your own name and age

  * These should be on the same line as where **binary_file** was changed in previous step

4. Save and exit `heart_rate_main.py`

5. Run one of the following from your command terminal

  * `python heart_rate_main.py`

  * `run heart_rate_main.py`

  * `execfile(heart_rate_main.py)`

  * **NOTE.** Different commands have been provided depending on the terminal being used, so if one does not work, have no fear, and try another!

6. What you should see while/after running:

  * Instantaneous heart rate should be printed to terminal

  * 1 minute average heart rates should be printed to terminal

  * 5 minute average heart rates should be printed to terminal

  * Warnings of bradycardia/tachycardia occurring should be printed to terminal

  * A new file should appear in your directory titled `heart_rate_output.txt` with all of the information printed to terminal logged for your convenience

7. In the case of an error, the following is one of the most likely reasons:

  * Input binary file does not use unsigned 16-bit int for all values (this includes the first value/sampling frequency)

  * Binary file was created in an unexpected format. The binary file created in for testing was made using the following command, which can be seen in `createTest.sh`:
    
    ** `echo -n -e \\x01\\x02\\x03 > test.bin`

  * Let the author of this files know of any other errors you encounter and they can be promptly fixed :)

8. Enjoy life!
