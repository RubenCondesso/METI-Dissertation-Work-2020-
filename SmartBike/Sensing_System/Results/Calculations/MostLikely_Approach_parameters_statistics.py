#
# MostLikely_Approach_parameters_statistics - Python file for the Sensing System
#
# 3 July 2020 - 1.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Calculate the parameters and get statistics for all data collected for the 'Most Likely' approach
#

from statistics import mean
from statistics import stdev
from statistics import variance
from matplotlib import pyplot as plt

import math



##################################################################################   Samples  ############################################################################################################################################################################################################################################################################################################################################################################################################


##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
#################################################################################  Regular Obstacle  #####################################################################################################################################################################################################################################################################################################################################################################################################

##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
########################################################   For 90 degrees Immobile - Regular obstacle at simulated scenario, with sensor 45cm high   ############################################################################################################################################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

#50cm
#data = [50.15, 50.27, 50.43, 50.47, 50.0, 50.03, 50.04, 50.01, 50.01, 50.05, 50.01, 50.03, 50.11, 50.05, 50.08, 50.07, 50.09, 50.03, 49.96, 49.99, 50.03, 50.07, 50.06, 49.95, 50.23, 50.01, 49.99, 50.06, 50.05, 50.02, 50.05, 50.1, 50.08, 50.06, 50.0, 50.01, 50.03, 49.94, 50.07, 50.02, 50.08, 49.99, 50.03, 50.06, 50.01, 50.03, 50.05, 50.09, 50.12, 49.97, 50.04, 50.11, 50.06, 50.1, 50.02, 50.01, 50.01, 50.06, 55.71, 50.04]

#100cm
#data = [99.86, 99.58, 99.78, 99.87, 99.71, 99.94, 99.6, 99.83, 99.52, 99.61, 99.47, 99.56,99.75, 99.62, 102.96, 99.83, 99.57, 99.55, 99.54, 99.56, 99.66, 99.64, 99.76, 99.67, 99.64, 99.56, 99.66, 99.5, 99.74, 99.62, 99.5, 99.67, 99.52, 99.34, 99.88, 99.59, 99.81, 99.48, 99.48, 99.68, 99.88, 102.09, 99.48, 99.57, 99.54, 99.44, 99.46, 99.4, 99.33, 99.51, 99.58, 99.69, 99.57, 99.68, 99.73, 99.66, 95.49, 100.84, 99.68, 91.64]

#150cm
#data = [148.09, 147.93, 148.01, 147.89, 147.81, 147.87, 147.9, 148.13, 147.88, 147.87, 147.94, 147.85, 148.0, 147.84, 147.9, 147.83, 148.27, 147.22, 148.01, 148.01, 147.87, 147.96, 148.22, 147.96, 147.98, 147.84, 148.09, 143.27, 148.08, 147.88, 148.02, 145.59, 147.86, 148.01, 147.84, 147.84, 147.99, 148.11, 147.96, 148.04, 148.31, 150.48, 150.65, 147.96, 141.19, 147.93, 147.04, 148.19, 148.6, 147.93, 147.86, 147.96, 147.93, 147.92, 146.88, 145.95, 147.87, 144.89, 145.92, 151.67]

#200cm
#data = [196.86, 196.64, 196.74, 194.62, 196.85, 197.06, 196.88, 197.14, 197.0, 196.9, 196.83, 196.8, 196.73, 196.6, 196.82, 196.72, 196.73, 196.69, 196.87, 196.93, 196.89, 196.95, 197.06, 197.8, 196.9, 196.98, 196.72, 196.89, 196.82, 196.75, 196.96, 189.79, 202.47, 194.1, 194.89, 212.66, 196.83, 196.9, 196.67, 196.74, 196.7, 196.93, 196.14, 190.25, 197.0, 197.07, 196.79, 205.32, 196.82, 196.82, 196.85, 196.84, 197.08, 196.99, 193.22, 197.06, 200.28, 198.13, 196.9, 207.43]

#250cm
#data = [246.35, 246.09, 245.98, 246.23, 246.09, 246.21, 246.24, 246.24, 246.19, 246.04, 246.04, 245.81, 246.05, 246.31, 246.03, 246.0, 246.08, 246.24, 246.17, 246.21, 246.28, 246.17, 246.2, 246.2, 246.09, 246.33, 245.96, 246.38, 246.23, 246.06, 246.13, 246.13, 246.09, 246.22, 234.61, 246.38, 247.05, 246.18, 246.12, 246.26, 246.07, 246.22, 246.21, 246.28, 249.41, 246.13, 246.07, 246.87, 246.16, 246.02, 246.25, 246.27, 246.09, 247.11, 242.86, 249.45, 246.06, 235.96, 246.22, 246.05]

#300cm
#data = [296.67, 296.66, 296.92, 296.76, 296.89, 296.82, 296.79, 296.89, 297.2, 296.6, 296.8, 296.87, 296.99, 297.0, 296.73, 296.78, 296.76, 296.69, 296.63, 297.44, 296.73, 296.99, 296.71, 296.74, 296.81, 296.87, 296.79, 296.77, 297.0, 296.91, 297.33, 296.86, 296.85, 296.98, 297.21, 296.98, 296.92, 296.93, 290.85, 296.99, 296.97, 296.8, 296.85, 296.85, 296.89, 296.95, 297.09, 296.87, 298.84, 296.81, 297.06, 296.8, 296.84, 297.07, 296.42, 296.88, 296.94, 289.78, 296.76, 296.95]

#350cm
#data = [288.41, 345.73, 345.18, 333.9, 345.1, 318.77, 347.95, 345.32, 318.54, 341.55, 332.56, 313.03, 336.94, 334.76, 324.82, 345.46, 333.6, 311.71, 249.21, 316.54, 345.28, 345.7, 342.26, 305.37, 335.34, 345.05, 340.25, 195.63, 314.72, 344.67, 262.39, 324.46, 300.22, 329.64, 318.06, 340.53, 218.55, 326.31, 304.15, 330.74, 262.81, 344.93, 311.98, 343.0, 345.77, 308.07, 334.12, 285.53, 308.41, 298.4, 347.89, 343.75, 312.6, 305.89, 311.15, 345.58, 307.65, 345.05, 340.18, 347.60]

#400cm
#data = [333.33, 363.84, 363.7, 325.7, 377.31, 359.04, 375.76, 344.27, 363.32, 374.48, 268.37, 311.83, 321.43, 345.85, 363.76, 344.85, 317.48, 345.07, 358.25, 329.19, 253.21, 326.26, 301.21, 373.85, 176.22, 173.53, 360.55, 367.89, 343.65, 374.7, 229.18, 236.34, 212.3, 338.04, 333.33, 205.93, 222.95, 210.76, 363.48, 382.1, 360.63, 230.49, 354.79, 239.02, 211.01, 321.94, 214.71, 374.63, 344.29, 352.37, 201.59, 304.07, 141.44, 261.02, 93.34, 200.6, 233.14, 277.93, 342.06, 361.49]



##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
########################################################   For 60 degrees Immobile - Regular obstacle at simulated scenario with sensor 45cm high   ##################################################################################################################################################################################################################################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

#50cm
#data = [50.67, 50.72, 50.57, 50.63, 50.69, 50.56, 50.69, 50.67, 50.74, 50.6, 50.59, 50.61, 50.58, 50.65, 50.62, 50.63, 50.66, 50.6, 50.67, 50.65, 50.65, 50.59, 50.58, 50.64, 50.58, 50.56, 50.64, 50.58, 50.6, 50.59, 50.6, 50.57, 50.63, 50.58, 50.66, 50.65, 50.59, 50.6, 50.59, 50.57, 50.59, 50.67, 50.66, 50.6, 50.61, 50.62, 50.71, 50.57, 50.6, 50.6, 50.61, 50.67, 50.78, 50.58, 50.58, 50.48, 50.44, 50.56, 50.67, 50.67]

#100cm
#data = [100.38, 100.43, 100.37, 99.9, 99.86, 100.28, 99.8, 99.85, 99.8, 100.11, 99.83, 100.52, 100.16, 99.8, 100.4, 100.16, 100.4, 100.1, 100.26, 100.19, 99.7, 99.84, 99.8, 100.16, 99.72, 100.03, 100.01, 99.93, 100.25, 100.32, 100.34, 100.61, 100.37, 100.02, 100.39, 100.56, 99.98, 106.5, 100.03, 100.02, 100.08, 100.64, 99.94, 100.17, 100.42, 99.98, 99.85, 99.78, 100.12, 100.37, 100.07, 100.04, 100.5, 100.14, 100.22, 99.81, 101.3, 100.03, 99.96, 100.06]

#150cm
#data = [150.63, 150.57, 150.63, 150.79, 150.66, 150.64, 150.91, 150.88, 150.82, 150.61, 150.64, 150.82, 146.04, 150.75, 150.75, 150.71, 150.83, 150.68, 150.61, 150.77, 147.08, 150.77, 151.03, 150.6, 148.98, 149.58, 150.75, 150.69, 150.37, 150.58, 150.73, 150.72, 150.86, 150.91, 150.61, 150.77, 150.89, 150.7, 152.28, 150.29, 154.24, 150.94, 151.43, 150.36, 150.69, 150.72, 151.05, 150.75, 150.65, 146.44, 150.76, 153.68, 150.06, 146.46, 150.66, 152.64, 144.98, 150.79, 150.82, 150.85]

#200cm
#data = [197.54, 197.44, 197.47, 197.27, 197.23, 197.41, 197.51, 197.58, 197.46, 197.66, 198.03, 197.35, 197.45, 197.34, 197.61, 197.18, 197.28, 197.4, 200.96, 197.54, 197.49, 198.4, 197.38, 197.63, 197.44, 197.36, 197.41, 197.66, 197.25, 197.55, 197.5, 197.4, 194.21, 197.5, 193.82, 202.51, 196.57, 198.41, 197.69, 197.49, 197.43, 197.48, 201.27, 195.42, 197.6, 190.07, 192.13, 196.51, 203.93, 197.5, 197.43, 197.31, 197.27, 197.41, 195.19, 183.05, 197.33, 193.68, 204.29, 197.39]

#250cm
#data = [247.25, 247.45, 247.62, 247.68, 247.5, 247.52, 247.36, 247.62, 247.55, 247.87, 247.63, 247.72, 247.64, 247.33, 247.6, 247.57, 247.61, 247.5, 247.53, 247.65, 249.05, 247.82, 247.41, 247.36, 247.62, 247.57, 247.81, 247.3, 247.44, 250.47, 247.4, 247.57, 245.91, 247.29, 247.46, 247.61, 247.61, 247.52, 247.75, 247.72, 247.65, 254.41, 242.06, 248.18, 244.63, 247.52, 247.52, 247.49, 247.64, 247.59, 251.85, 249.47, 240.32, 246.87, 246.3, 247.62, 247.74, 247.64, 248.14, 252.56]

#300cm
#data = [296.19, 295.98, 296.44, 296.22, 296.39, 296.55, 296.3, 296.31, 296.61, 296.19, 296.38, 296.25, 296.19, 296.35, 296.19, 296.39, 296.55, 296.33, 296.49, 296.18, 296.42, 296.1, 296.43, 296.18, 296.15, 296.3, 296.38, 302.33, 296.92, 296.34, 296.9, 296.58, 296.62, 296.26, 296.29, 296.33, 296.2, 296.43, 296.39, 296.38, 296.36, 296.45, 298.33, 296.3, 295.64, 297.15, 296.58, 296.3, 296.35, 296.47, 296.11, 296.4, 300.22, 295.27, 300.38, 297.57, 296.09, 296.36, 296.06, 296.28]

#350cm
#data = [336.13, 324.29, 332.75, 322.63, 345.5, 347.07, 346.87, 307.09, 208.28, 280.31, 235.84, 345.51, 319.13, 299.55, 319.23, 343.41, 314.63, 315.53, 313.82, 331.83, 243.57, 308.84, 158.37, 315.17, 293.07, 290.85, 342.24, 333.26, 311.94, 319.74, 251.88, 317.99, 348.07, 329.68, 310.65, 296.95, 296.77, 295.21, 310.6, 304.87, 227.65, 333.98, 220.76, 219.12, 331.78, 296.47, 328.79, 298.27, 289.95, 302.52, 280.01, 298.8, 32.27, 303.01, 192.4, 307.67, 317.78, 334.65, 281.51, 167.0]

#400cm
#data = [NA]




##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
#################################################################################  Irregular Obstacle  #######################################################################################################################################################################################################################################################################################################################################################################################################################

##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
########################################################   For 90 degrees Immobile - Irregular obstacle at simulated scenario, with sensor 45cm high   ##################################################################################################################################################################################################################################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

#50cm
#data = [59.29, 62.31, 62.75, 54.13, 60.68, 58.4, 61.9, 64.22, 62.84, 60.34, 95.37, 71.7, 62.5, 65.14, 60.02, 66.17, 89.91, 56.61, 59.24, 60.24, 61.72, 88.48, 85.24, 89.78, 90.86, 92.03, 92.11, 90.67, 56.69, 56.5, 61.0, 79.19, 94.66, 64.74, 88.66, 68.93, 57.16, 59.36, 91.46, 61.61, 94.26, 88.03, 87.34, 58.88, 77.73, 59.52, 74.68, 93.35, 63.15, 79.37, 65.06, 93.33, 57.92, 89.15, 56.51, 88.65, 56.92, 58.61, 56.25, 61.04]

#100cm
#data = [100.98, 101.15, 100.95, 100.41, 101.33, 100.24, 100.62, 100.19, 101.13, 101.18, 100.31, 101.11, 100.48, 101.4, 101.26, 101.43, 101.91, 101.55, 101.21, 100.89, 100.46, 101.16, 101.08, 101.15, 100.73, 100.98, 101.05, 100.34, 101.17, 100.18, 101.24, 100.12, 101.18, 100.01, 101.36, 100.56, 101.34, 100.99, 100.93, 101.1, 101.14, 100.61, 98.99, 100.84, 100.62, 98.44, 101.44, 100.81, 100.94, 101.28, 100.34, 100.88, 100.76, 101.37, 101.72, 100.34, 101.05, 99.63, 100.46, 100.96, 99.83, 101.22, 100.17, 100.59, 100.26, 101.01]

#150cm
#data = [150.86, 150.69, 150.45, 151.2, 150.65, 150.88, 149.72, 150.88, 150.9, 150.67, 145.98, 150.89, 151.04, 150.56, 147.53, 150.8, 151.04, 149.89, 150.86, 150.74, 152.0, 151.56, 151.89, 150.16, 151.18, 151.29, 151.44, 150.36, 151.28, 146.68, 141.79, 150.92, 151.09, 146.0, 150.39, 150.92, 148.67, 151.1, 151.51, 151.15, 150.52, 151.09, 150.86, 144.16, 153.8, 142.04, 144.66, 142.87, 150.19, 151.16, 151.47, 151.53, 146.06, 150.67, 145.68, 148.69, 149.54, 142.41, 153.85, 155.18, 145.62, 151.16, 157.33]

#200cm
#data = [204.24, 191.39, 177.02, 263.55, 200.45, 214.8, 167.33, 299.03, 214.03, 194.3, 206.5, 198.08, 300.2, 194.7, 172.29, 434.99, 206.96, 163.67, 151.01, 199.65, 205.15, 173.3, 207.21, 174.82, 211.57, 193.82, 187.74, 377.86, 189.82, 249.26, 202.29, 208.61, 198.3, 215.37, 198.91, 204.91, 213.28, 169.39, 100.78, 228.63, 140.64, 159.61, 211.24, 205.65, 409.85, 170.66, 216.09, 195.19, 144.25, 194.34, 197.59, 199.31, 160.15, 201.84, 211.76, 151.67, 145.65, 145.73, 211.49, 125.65]

#250cm
#data = [327.47, 309.5, 446.11, 212.15, 271.05, 244.19, 297.14, 187.6, 376.37, 337.34, 262.64, 416.34, 382.69, 236.58, 418.63, 320.46, 272.64, 435.3, 344.16, 225.35, 316.83, 388.11, 362.44, 275.04, 230.17, 377.55, 280.01, 198.07, 263.73, 307.26, 344.11, 225.18, 156.7, 424.04, 218.52, 319.31, 349.48, 358.23, 306.05, 162.31, 339.0, 299.35, 438.36, 416.26, 231.17, 344.61, 342.29, 320.81, 335.54, 190.58, 124.11, 236.5, 390.65, 283.95]

#300cm
#data = [NA]

#350cm
#data = [NA]

#400cm
#data = [NA]



##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
########################################################   For 60 degrees Immobile - Irregular obstacle at simulated scenario, with sensor 45cm high   ##################################################################################################################################################################################################################################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

#50cm
#data = [95.7, 69.88, 71.56, 69.0, 87.73, 70.24, 94.82, 83.27, 94.32, 123.15, 70.75, 70.54, 80.54, 70.82, 70.23, 99.35, 70.76, 70.24, 70.28, 70.46, 70.4, 70.61, 97.51, 70.46, 70.73, 94.82, 70.36, 97.15, 90.14, 89.01, 116.92, 70.62, 82.15, 79.01, 67.63, 93.7, 70.3, 81.45, 77.06, 71.14, 70.62, 79.59, 69.52, 70.66, 72.45, 71.18, 71.56, 70.25, 70.09, 71.34, 75.01, 72.14, 70.01, 80.67, 69.81, 75.2, 70.28, 103.69, 89.38, 183.38]

#100cm
#data = [100.13, 101.79, 101.72, 101.21, 101.25, 101.78, 101.52, 101.41, 101.65, 101.31, 101.71, 101.47, 102.21, 101.66, 101.55, 100.98, 101.33, 101.24, 101.7, 101.55, 100.21, 101.92, 100.83, 101.11, 100.42, 101.28, 101.62, 101.41, 101.56, 101.02, 101.77, 101.69, 102.1, 101.35, 100.96, 101.39, 101.2, 101.08, 100.58, 94.78, 100.81, 100.82, 101.97, 101.65, 101.77, 101.45, 101.31, 100.82, 101.16, 101.82, 102.61, 101.56, 102.19, 100.62, 100.71, 101.21, 98.78]

#150cm
#data = [207.05, 169.58, 148.3, 162.2, 147.71, 155.38, 143.34, 321.0, 439.63, 192.76, 148.37, 161.03, 155.39, 205.46, 142.7, 205.79, 319.99, 240.65, 192.79, 209.45, 409.18, 157.44, 149.46, 146.53, 154.42, 354.44, 188.21, 146.55, 150.19, 152.17, 134.18, 156.93, 153.17, 112.49, 156.7, 153.68, 270.1, 155.67, 151.62, 172.01, 158.38, 152.88, 157.98, 154.23, 144.12, 145.26, 149.53, 159.89, 151.26, 157.04, 152.0, 156.52, 128.34, 148.38, 156.62, 116.26, 140.68, 157.03, 156.99, 150.41]

#200cm
#data = [NA]

#250cm
#data = [NA]

#300cm
#data = [NA]

#350cm
#data = [NA]

#400cm
#data = [NA]




##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
##################################################################################   Timelines  ########################################################################################################################################################################################################################################################################################################################################################################################################################

# Normal timeline
#x = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 93, 95, 97, 99, 101, 103, 105, 107, 109, 111, 113, 115, 117, 119]



##################################################################################   Paramaters  ########################################################################################################################################################################################################################################################################################################################################################################################################################

plt.scatter(x, data, c='red', marker = '^')
plt.xlabel("Time instance in seconds")
plt.ylabel("Distance measured in meters")
plt.title("Distances measured at ??cm at ?? degrees, w/ sensor ??cm high")


minnumber = min(data)
print("Min number is: ", minnumber)

maxnumber = max(data)
print("Max number is: ", maxnumber)

x = mean(data)
print("Mean is: ", x)

y = stdev(data)
print("Standard deviation is : ", y)

z = variance(data)
print("Variance is: ", z)

er = y/(math.sqrt(60))
print("Standard Error: ", er)

plt.show()



