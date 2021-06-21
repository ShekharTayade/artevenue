#!/usr/bin/env python
# coding: utf-8

# In[108]:


from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np
import math
import cv2

def tilt_image(img, flag):
        
    def find_coeffs(source_coords, target_coords):
        matrix = []

        for s, t in zip(source_coords, target_coords):
            matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
            matrix.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])

        A = np.matrix(matrix, dtype=np.float)
        B = np.array(source_coords).reshape(8)
        X = np.dot(numpy.linalg.inv(A.T * A) * A.T, B)

        return np.array(X).reshape(8)

    img = np.array(img) 
    img = img[:, :, ::-1].copy() 
    
    width = img.shape[1]
    height = img.shape[0]
    
    theta = 10
    s = width/height
    if s >= 2:
        theta = 20
    elif s <= 0.5:
        theta = 1

    r = 0.5*(1-1/(1+1/s*math.tan(theta*math.pi/180)))
    R = 0.5*(1+1/(1+1/s*math.tan(theta*math.pi/180)))

    new_height = [height*r, (R*height)]
    new_width = width*math.cos(theta*math.pi/180)
   
    inp_coordinates = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    output_coordinates = np.float32([[0, 0], [new_width, new_height[0]], [new_width, new_height[1]], [0, height]])

    matrix = cv2.getPerspectiveTransform(inp_coordinates,output_coordinates)

    imgOutput = cv2.warpPerspective(img, matrix, (width,height), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=[255,255,255,0])

    imgOutput = cv2.cvtColor(imgOutput, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(imgOutput)

    #Creating image border
    img_border = img.crop((0, 0, 10, height))
    
    border_imgOutput = img_border
    width1, height1 = img_border.size
    
    theta1 = theta/6
    
    if s>1:
        theta1 = theta/3
        
    r1 = 0.5*(1-1/(1+1/s*math.tan(theta1*math.pi/180)))
    R1 = 0.5*(1+1/(1+1/s*math.tan(theta1*math.pi/180)))

    new_height1 = [height1*r1, (R1*height)]
    new_width1 = width1*math.cos(theta1*math.pi/360)
    img_border = np.array(img_border) 
    img_border = img_border[:, :, ::-1].copy() 
    
    border_inp = np.float32([[0, 0], [width1, 0], [width1, height1], [0, height1]])
    border_out = np.float32([[0, 0], [new_width1, new_height1[0]], [new_width1, new_height1[1]], [0, height1]])

    border_matrix = cv2.getPerspectiveTransform(border_inp,border_out)
    img_border = cv2.warpPerspective(img_border, border_matrix, (width1,height1), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=[255,255,255,0])

    #Creating mirror image of border
    img_border = cv2.flip(img_border, 1)       
    img_border = cv2.cvtColor(img_border, cv2.COLOR_BGRA2RGB)
    img_border = Image.fromarray(img_border) 
    
    #Darkening image
    enhancer = ImageEnhance.Brightness(img_border)
    img_border = enhancer.enhance(0.7)

    img_border = np.array(img_border) 
    img_border = img_border[:, :, ::-1].copy() 
    img_border = cv2.cvtColor(img_border, cv2.COLOR_BGRA2RGB)

    for i in range(len(img_border)):
        for j in range(10):
            if (img_border[i][j][0] == 178):
                img_border[i][j] = [255, 255, 255]
        if (not flag):
            for k in range(5):
                if (img_border[i][k] != 255).all():
                    img_border[i][k] = [246,246,200]

    #Merging border and tilted image
    image = cv2.hconcat([img_border, imgOutput])
    
    #Improving resolution
    sr = cv2.dnn_superres.DnnSuperResImpl_create()

    path = "FSRCNN_x2.pb"
    sr.readModel(path)
    sr.setModel("fsrcnn",2)
    result = sr.upsample(image)  
    result = cv2.resize(image,(width, height), interpolation = cv2.INTER_NEAREST)
    image = Image.fromarray(result)
    
    return image

