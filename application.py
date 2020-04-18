import base64
import io
import json
import os
import sys

import cv2 as cv
import jsonpickle
import numpy as np
import requests
from flask import Flask, Response, jsonify, request
from PIL import Image, ImageFont, ImageDraw
from titlecase import titlecase

def analyze_img(rdata):
    #receive base64 encoded string and convert it to binary
    decoded_data = base64.b64decode(rdata)
    #convert binary image to numpy array
    np_data = np.frombuffer(decoded_data,np.uint8)
    #encode numpy array to jepg image
    image = cv.imdecode(np_data,cv.IMREAD_UNCHANGED)
    
    url = "https://microsoft-azure-microsoft-computer-vision-v1.p.rapidapi.com/analyze"

    querystring = {"visualfeatures":"Categories,Tags,Color,Faces,Description"}
    #sending the converted binary image
    payload = decoded_data
    headers = {
        'x-rapidapi-host': "microsoft-azure-microsoft-computer-vision-v1.p.rapidapi.com",
        'x-rapidapi-key': "f5cf55a5c2msh4f27fe5644b39bdp157623jsn37b8f0da0884",
        'content-type': "application/octet-stream"
        }
    
    resp = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    
    loaded_json = json.loads(resp.text)
    
    faces = loaded_json['faces']
    num_face = len(faces)
    desc = loaded_json['description']
    img_title = titlecase(desc['captions'][0]['text'])

    tags = ', '.join([i for i in desc['tags'][0:8]])

    x1=np.zeros(num_face)
    y1=np.zeros(num_face)
    x2=np.zeros(num_face)
    y2=np.zeros(num_face)
    age = np.zeros(num_face)
    gender = list()

    for i in range(0,num_face):
        x1[i] = faces[i]['faceRectangle']['left']
        y1[i] = faces[i]['faceRectangle']['top']
        x2[i] = faces[i]['faceRectangle']['width'] + x1[i]
        y2[i] = faces[i]['faceRectangle']['height'] + y1[i]
        age[i] = faces[i]['age']
        gender.append(faces[i]['gender'])
        
    #drawing and naming face rectangles
    for i in range(0,num_face):
        cv.rectangle(image,(int(x1[i]),int(y1[i])),(int(x2[i]),int(y2[i])),(255,255,255),2)
        #cv.putText(image, (gender[i] +" "+ str(int(age[i]))) , (int(x1[i]), int(y1[i])-5), cv.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255), 1)
    
    fontpath = "./Roboto-Medium.ttf"     
    font = ImageFont.truetype(fontpath, 22)
    
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)
    for i in range(0,num_face):
        if (int(y1[i])-25)>0:
            box_area = image[int(y1[i])-25:int(y1[i]),int(x1[i]):int(x2[i])]
            textLoc = (int(x1[i]), int(y1[i])-25)
            shadowLoc = (int(x1[i])+2, int(y1[i])-23)
        elif (int(y1[i]))>0:
            box_area = image[0:int(y1[i]),int(x1[i]):int(x2[i])]
            textLoc = (int(x1[i]), int(y1[i])-25)
            shadowLoc = (int(x1[i])+2, int(y1[i])-23)
            
        elif (int(y1[i]))==0:
            box_area = image[int(y2[i]):int(y2[i])+25,int(x1[i]):int(x2[i])]
            textLoc = (int(x1[i]), int(y2[i])+5)
            shadowLoc = (int(x1[i])+2, int(y2[i])+7)
        
            
        box_area = cv.cvtColor(box_area,cv.COLOR_BGR2GRAY)
        ret,thresh = cv.threshold(box_area,127,255,cv.THRESH_BINARY)
        average = np.sum(thresh)/thresh.size
        if average<127:
            textColor = (255,255,255,0)
        else:
            textColor = (0,0,0,0)
        draw.text(shadowLoc,  gender[i] +" "+ str(int(age[i])), font = font, fill = (100,100,100,100))
        draw.text(textLoc,  gender[i] +" "+ str(int(age[i])), font = font, fill = textColor)
        
    image = np.array(img_pil)
    #converting jpeg to binary image
    image = cv.imencode(".jpg",image)[1].tostring()
    #converting binary to base64
    img_base64 = base64.b64encode(image)
    
    return img_base64, img_title, tags

# Initialize the Flask application
application = Flask(__name__)

# route http posts to this method
@application.route('/test',methods=['POST'])
def test():
    r = request

    try:
        img_base64,img_title,tags = analyze_img(r.data)
        return jsonify({'Image':str(img_base64),'Image_Title':img_title,'Image_Tags':tags})
    except:
        return jsonify({'status':'An exception occurred'})
@application.route('/',methods=['GET','POST'])
def main():
    return({'status':'Working'})

# start flask app
if __name__ == "__main__":
    application.run()

