import numpy as np

def reMap(value, maxInput, minInput, maxOutput, minOutput, negativeAsMax=False):

    if negativeAsMax:
        value = maxInput if value < 0.0 else value

    value = maxInput if value > maxInput else value
    value = minInput if value < minInput else value
    
    inputSpan = maxInput - minInput
    outputSpan = maxOutput - minOutput
    scaledThrust = float(value - minInput) / float(inputSpan)
    return minOutput + (scaledThrust * outputSpan)

def sample_coordinate(point:tuple[float, float], img_res:tuple[float, float], city_size:tuple[float, float]):
        x_loc = city_size[0] / img_res[0] * point[0]
        y_loc = city_size[1] / img_res[1] * point[1]

        return x_loc, y_loc

def separate_by_color(img, color, tolerance = 5):
        img_array = np.array(img)

        maskRed = np.bitwise_and(img_array[...,0] <= color[0] + tolerance, img_array[...,0] >= color[0] - tolerance)

        maskGreen = np.bitwise_and(img_array[...,1] <= color[1] + tolerance, img_array[...,1] >= color[1] - tolerance)

        maskBlue = np.bitwise_and(img_array[...,2] <= color[2] + tolerance, img_array[...,2] >= color[2] - tolerance)
        maskCombined = maskRed & maskGreen & maskBlue
        img_array[maskCombined] = [255, 255, 255]
        
        img_array[np.invert(maskCombined)] = [0, 0, 0]
        return img_array