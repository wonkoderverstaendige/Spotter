# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 14:45:41 2012

@author: Ronny
"""
from sys import float_info

def BGRpix2HSV( pixel ):
    """ Converts BGR color information of a single pixel to HSV """
    B = pixel[0]/255.
    G = pixel[1]/255.
    R = pixel[2]/255.
    
    V = max(R, G, B)

    # This requires some corner case handling when V or S get 0 to avoid
    # div by Zeros, will be rounded away upon return again
    if V < 2*float_info.epsilon:
        S = float_info.epsilon
    else:
        S = (V-min(R, G, B))/V
        if S < 2*float_info.epsilon:
            S = float_info.epsilon
    
    if V == R:
        H = 60 * (G-B)/S
    elif V == G:
        H = 120 + 60 * (B-R)/S
    elif V == B:
        H = 240 + 60 * (R-G)/S

    if H < 0:
        H += 360

    H /= 2.
    S *= 255.
    V *= 255.   

    return int(H), int(S), int(V)
    
