def listAverage(n1, n2):
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