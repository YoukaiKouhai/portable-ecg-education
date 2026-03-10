import numpy as np

def derive_12_leads(I, II):

    III = II - I

    aVR = -(I + II)/2
    aVL = I - II/2
    aVF = II - I/2

    V1 = I*0.2
    V2 = I*0.4
    V3 = I*0.6
    V4 = I*0.8
    V5 = I
    V6 = II

    return {
        "I":I,
        "II":II,
        "III":III,
        "aVR":aVR,
        "aVL":aVL,
        "aVF":aVF,
        "V1":V1,
        "V2":V2,
        "V3":V3,
        "V4":V4,
        "V5":V5,
        "V6":V6
    }