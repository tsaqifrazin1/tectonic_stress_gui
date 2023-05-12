import re
import pandas as pd
import numpy as np
import math
import os

def calculate_cfs(fric, normal, shear):
    return abs(shear) + (fric * normal)

def stress_from_strain_skripsi(tau_xx, tau_yy, tau_xy, modulus_elastisitas, poisson_ratio):
    tau_one_three = [[tau_xx], [tau_yy], [tau_xy]]
    c = modulus_elastisitas/((1+poisson_ratio)*(1-2*poisson_ratio))
    m1 = np.array([[1-poisson_ratio, poisson_ratio,0],[poisson_ratio,1-poisson_ratio,0],[0,0,1-2*poisson_ratio]])
    c1 = c * m1
    return np.dot(c1, tau_one_three)

def stress_from_disertasi(miu, lamda, tau_xx, tau_yy, tau_xy):
    tau = np.array([
        [tau_xx, tau_xy],
        [tau_xy, tau_yy]
    ])

    return (lamda *(tau_xx + tau_yy) *np.identity(2)) + (2*miu*tau)

def principal_stress_from_liu(tau_xx, tau_yy, modulus_elastisitas, poisson_ratio):
    b = -1 *(modulus_elastisitas*tau_yy)
    c = -1 *((modulus_elastisitas*tau_yy)/((1+poisson_ratio)*tau_xx))
    a = 1
    sigma2a = ((-1 * b) + np.sqrt(b**2 - 4*a*c))/2*a
    sigma2b = ((-1 * b) - np.sqrt(b**2 - 4*a*c))/2*a
    sigma11 = tau_xx*modulus_elastisitas - (modulus_elastisitas/((1+poisson_ratio)*sigma2a))
    sigma12 = tau_xx*modulus_elastisitas - (modulus_elastisitas/((1+poisson_ratio)*sigma2b))

    epsilon11 = (sigma11 - (modulus_elastisitas/((1+poisson_ratio)*sigma2a)))/modulus_elastisitas
    epsilon12 = (sigma2a - (modulus_elastisitas/((1+poisson_ratio)*sigma11)))/modulus_elastisitas

    epsilon21 = (sigma12 - (modulus_elastisitas/((1+poisson_ratio)*sigma2b)))/modulus_elastisitas
    epsilon22 = (sigma2b - (modulus_elastisitas/((1+poisson_ratio)*sigma12)))/modulus_elastisitas

    if((epsilon11 <= tau_xx + 0.001 and epsilon11 >= tau_xx - 0.001) and (epsilon12 <= tau_yy + 0.001 and epsilon12 >= tau_yy - 0.001)):
        return sigma11, sigma2a
    if((epsilon21 <= tau_xx + 0.001 and epsilon21 >= tau_xx - 0.001) and (epsilon22 <= tau_yy + 0.001 and epsilon22 >= tau_yy - 0.001)):
        return sigma12, sigma2b
    return ValueError

def principal_stress_from_eig(tau_xx, tau_yy, tau_xy):
    tau = np.array([
        [tau_xx, tau_xy],
        [tau_xy, tau_yy]
    ])

    w,v = np.linalg.eig(tau)

    return w,v

def principal_stress_from_pdf(tau_xy, sigma_xx, sigma_yy):
    sigma1 = (sigma_xx + sigma_yy) + (np.sqrt(((sigma_xx - sigma_yy)/2)**2) - tau_xy**2)
    sigma2 = (sigma_xx + sigma_yy) - (np.sqrt(((sigma_xx - sigma_yy)/2)**2) - tau_xy**2)
    return sigma1, sigma2

def theta_from_pdf(tau_xy, sigma_xx, sigma_yy):
    theta = np.arctan(((2*tau_xy/(sigma_xx - sigma_yy))* np.pi/180)/2)
    return theta

def normal_and_shear_from_ppt(sigma1, sigma2, theta):
    normal = ((sigma1 + sigma2)/2) + ((sigma1 - sigma2)/2)*math.cos(theta)
    shear = ((sigma1 - sigma2)*math.sin(theta))/2
    return normal, shear

def normal_and_shear_from_liu(sigma1, sigma2, theta):
    coscutheta = (math.cos(theta)**2)
    sincutheta = (math.sin(theta)**2)
    sin2theta = (math.sin(theta*2))
    normal = sigma1*coscutheta + sigma2*sincutheta
    shear = ((sigma2-sigma1)*sin2theta)/2

    return normal, shear

def normal_and_shear_from_pdf(sigma1, sigma2, stress_xy, theta):
    normal = ((sigma1 + sigma2)/2) + (sigma1 - sigma2)/2*np.cos(2*theta*np.pi/180) + stress_xy*np.sin(2*theta*np.pi/180)
    shear = (sigma1 - sigma2)/2*np.sin(2*theta*np.pi/180) + stress_xy*np.cos(2*theta*np.pi/180)
    return normal, shear

def average_segment(dir, segment):
    if(os.path.exists(dir) == False):
        return ValueError("File {} not found".format(dir))
    file = pd.read_table(dir, header=None, delim_whitespace=True)
    sum = 0
    tot = 0
    for j in range(0,len(file)):
        if(pd.isna(file[2][j]) == False):
            sum = sum + file[2][j]
            tot = tot + 1
    return sum/tot
