def myAverage(n1, n2):
    """
    This function calculates the average of two integers
    If one of the input numbers is not an integer a zero is returned
    
    :param int n1: number one
    :param int n2: number two
    :return int a: calculated average
    """
    if type(n1) != int or type(n2) != int:
        return 0
        
    a = myRound((n1 + n2) / 2)
    return a
    
def myRound(n):
    """
    This function rounds a number up if it has decimal >= 0.5
    
    :param float n: input number
    :return int r: rounded number
    """
    if n % 1 >= 0.5:
        r = int(n) + 1
    else:
        r = int(n)
        
    return r
    
def listAverage(input_list):
    """
    This function finds the average value in a list
    
    :param list input_list: a list of all integer values
    :return float average: calculated list average
    """
    if len(input_list) < 1:
        print("\nCannot take average. List has length=0\n")
        raise IndexError

    denominator = len(input_list)
    
    numerator = 0
    for i in range(denominator):
        if type(input_list[i]) != int:
            print("\nList must only consist of integer values\n")
            raise TypeError
        numerator += input_list[i]
        
    average = numerator / denominator
    
    return average
    
def listInts(input_list):
    """
    This function takes a list of ints and/or floats and converts all values to
    type int
    
    :param list input_list: list of ints and/or floats
    :return list int_list: list of only ints
    """
    for i in range(len(input_list)):
        try:
            input_list[i] = int(input_list[i])
        except (TypeError, ValueError):
            print("\nValues in input list must be types int or float\n")
            raise TypeError
    
    int_list = input_list
    
    return int_list
            