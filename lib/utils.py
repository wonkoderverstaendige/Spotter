# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 14:45:41 2012

@author: Ronny
"""

def RGBpix2HSV( pixel ):
    """ Converts RGB color information of a single pixel to HSV """
    R = pixel[0]/255.
    G = pixel[1]/255.
    B = pixel[2]/255.
    
    V = max(R, G, B)
    print V
    
    if V == 0:
        S = 0
    else:
        S = (V-min(R, G, B))/V
        print(S)
    
    if V == R:
        H = 60 * (G-B)/S
    elif V == G:
        H = 120 + 60 * (B-R)/S
    elif V == B:
        H = 240 + 60 * (R-G)/S

    if H < 0:
        H += 360

    H /= 2
    S *= 255
    V *= 255    
    
    return int(H), int(S), int(V)
    
