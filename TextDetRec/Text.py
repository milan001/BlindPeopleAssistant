
from PIL import Image
import pytesseract
from gtts import gTTS
import os
import re,string
import cv2
import sys


def captch_ex(file_name):
    img = cv2.imread(file_name)
    
    img_final = cv2.imread(file_name)
    img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 160, 255, cv2.THRESH_BINARY)
    
    image_final = cv2.bitwise_and(img2gray, img2gray, mask=mask)
    
#    if(sys.argv[2]=='0'):
    ret, new_img = cv2.threshold(image_final, 160, 255, cv2.THRESH_BINARY)
#    else:
#        ret, new_img = cv2.threshold(image_final, 160, 255, cv2.THRESH_BINARY_INV)

      # for black text , cv.THRESH_BINARY_INV

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,
                                                         3))# to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
    dilated = cv2.dilate(new_img, kernel, iterations=9)  # dilate , more the iteration more the dilation

    # get contours
    image, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    for contour in contours:
         # get rectangle bounding contour
         [x, y, w, h] = cv2.boundingRect(contour)
         
         # Don't plot small false positives that aren't text
         if w < 40 and h < 40:
             continue
                 
         # draw rectangle around contour on original image
#         cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)




         crop_img = img_final[y:y+h, x:x+w]
         
         cv2_im = cv2.cvtColor(crop_img,cv2.COLOR_BGR2RGB)
         pil_im = Image.fromarray(cv2_im)

         text = pytesseract.image_to_string(pil_im, lang = 'eng')
         


#         no_punct = ""
#         for char in text:
#            if char not in punctuations:
#                no_punct = no_punct + char

         
         no_punct = ''.join(c for c in text if c not in string.punctuation)
         
         # display the unpunctuated string
         if(len(no_punct)>3 and no_punct.isupper()):
              cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)
              no_punct=no_punct.replace('\n', ' ')
              no_punct=re.sub(' +',' ',no_punct)
              print(no_punct)
              tts = gTTS(no_punct.lower()+" is written in your front.", lang='en')
              tts.save("audio.mp3")
              os.system("mpg321 audio.mp3")
#              os.system("say "+no_punct+" is written in your front.")

         cv2.imwrite('out.jpg',img)


if(len(sys.argv)<2):
    print("Input Image Name as command line argument.")
    exit()

file_name = sys.argv[1]
captch_ex(file_name)
