""" Module to control the UV lamp.
function:
    distance_to_On_time: calculates ON time for UV lamp using polynomial model of distance.
"""
# Log:
#   - Current code uses minimum irradiance (worst case scenatio, longest time). 
#   - TODO:
#       - Confirm units with Optics Team. 
#       - Confirm usage of min/max/average irradiance
#       - Check static vs dynamic. 

# Last edit: Jordan Hong, 21:30 July 22, 2020 

# minIrradTime is the constants associated with the ith power of a polynomical with x as distance
minIrradTime = [320.25, -76.859, 444.6, -72.298]

def distance_to_On_time (dist, theta):
    """
    Computes time ON time for UV lamp. 
    
    :param  int     dist:   distance of lamp to surface (m). Must be within 0.5m to 3m.
    :theta  list    theta:  list of constants associated with polynomial.
    :return int onTime: time for lamp to be turned on (s).
    """
    # Limits
    minDist = 0.5
    maxDist = 3

    # Error check 
    if (dist < minDist) or (dist>maxDist):
        print("Error. Distance out of range. Exiting")
        return -1

    # Compute on time via polynomial expression
    onTime = 0

    deg_lim = len(theta) # define degree limit
    for i in range (0, deg_lim, 1):
        onTime += theta[i] * (dist**i)

    return onTime


def test_distance_to_On_time():
    distance_list = [0.5, 1, 1.5, 2, 2.5, 3]
    
    for dist in distance_list:
        time = distance_to_On_time(dist, minIrradTime)
        print("Distance: %f; ON time: %f" %(dist, time))

    return True


if __name__ == "__main__":
    test_distance_to_On_time()
