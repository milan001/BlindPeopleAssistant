
import cv2
import sys
import os
import re


tracker = cv2.TrackerMedianFlow_create()

def bb_intersection_over_union(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0]+boxA[2],boxB[0]+ boxB[2])
    yB = min(boxA[1]+boxA[3],boxB[1]+ boxB[3])
    
    # compute the area of intersection rectangle
    interArea = (xB - xA + 1) * (yB - yA + 1)
    
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    
    # return the intersection over union value
    return iou




# Read video
#video = cv2.VideoCapture("t3.mp4")

if(len(sys.argv)<2):
    print("Input Video Name as command line argument.")
    exit()


video=cv2.VideoCapture(sys.argv[1])


# Exit if video not opened.
if not video.isOpened():
    print ("Could not open video")
    sys.exit()

#Get number of frames in video
length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

os.chdir("darknet")

nframes=20

prevBbox=[]

for i in range(int(length/nframes)):
    
    # Read  frame.
    ok, frame = video.read()
    if not ok:
        print ('Cannot read video file')
        sys.exit()


    cv2.imwrite('tem.jpg',frame)

    os.system("./darknet detector test cfg/voc.data cfg/tiny-yolo-voc.cfg tiny-yolo-voc.weights "+"tem.jpg"+" > tmp.txt")
    
    f = open("tmp.txt", "r")

    temp=0
    crop=[]
    s=0

    bbox=[]

    for line in f:
        wordList = re.sub("[^\w]", " ",  line).split()

        if temp==1:
            bbox.append(map(int, re.findall(r'\d+', line)))
            s=s+1
            temp=0
        if wordList[0]=="car" and int(wordList[1])>=30:
            temp=1


    if(s==0):
        for i in range(nframes):
            ok, frame = video.read()
            cv2.imshow("Tracking", frame)
            k = cv2.waitKey(1) & 0xff
            if k == 27 :
                break
        continue


    tracker=[None]*len(bbox)
    center=[None]*len(bbox)
    marked=[None]*len(bbox)
    area=[None]*len(bbox)
    arBool=[None]*len(bbox)


    for i in range(len(bbox)):
        
        marked[i]=0
        arBool[i]=0
        
        bbox[i]=list(bbox[i])
        
        for j in range(len(prevBbox)):
            if(bb_intersection_over_union(bbox[i],prevBbox[j])>0.9):
                marked[i]=prevMark[j]
                if(prevBbox[j][2]*prevBbox[j][3] < bbox[i][2]*bbox[i][3]):
                    arBool[i]=1


        bbox[i][2]=bbox[i][2]-bbox[i][0]
        bbox[i][3]=bbox[i][3]-bbox[i][1]
        bbox[i]=tuple(bbox[i])
        area[i]=bbox[i][2]*bbox[i][3]
        center[i]=(bbox[i][0]+(bbox[i][2]/2),bbox[i][1]+(bbox[i][3]/2))

        p1 = (int(bbox[i][0]), int(bbox[i][1]))
        p2 = (int(bbox[i][0] + bbox[i][2]), int(bbox[i][1] + bbox[i][3]))
        cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
        print(bbox[i])
        

        # Initialize tracker with first frame and bounding box
        tracker[i] = cv2.TrackerMedianFlow_create()
        ok = tracker[i].init(frame, bbox[i])
        print(marked[i],".........................")



    for i in range(len(bbox)):
        if(marked[i]>=3):
            os.system("say A car is coming towards you. Please move aside.")
#            tts = gTTS("A car is coming towards you. Please move aside.", lang='en')
#            tts.save("audio.mp3")
#            os.system("mpg321 audio.mp3")


    cv2.imshow("Tracking", frame)
    coun=0

    m=0

    while coun<nframes:
        
        coun=coun+1
        # Read a new frame
        ok1, frame = video.read()
        if not ok1:
            break

        # Start timer
        timer = cv2.getTickCount()

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);


        bbox = [None] * len(tracker)
        ok = [None] * len(tracker)
        centerFin=[None]*len(bbox)
        areaFin=[None]*len(bbox)

        # Update tracker
        for i in range(len(tracker)):
            ok[i], bbox[i] = tracker[i].update(frame)
            
            if ok:
                centerFin[i]=(bbox[i][0]+(bbox[i][2]/2),bbox[i][1]+(bbox[i][3]/2))
                areaFin[i]=bbox[i][2]*bbox[i][3]
   
                if (abs(centerFin[i][0]-center[i][0])<50 and areaFin[i]>area[i]):
                    if(m==0):
                        m=1
                        marked[i]=marked[i]+1
                    # Tracking success
                    p1 = (int(bbox[i][0]), int(bbox[i][1]))
                    p2 = (int(bbox[i][0] + bbox[i][2]), int(bbox[i][1] + bbox[i][3]))
                    cv2.rectangle(frame, p1, p2, (100,0,0), 2, 1)
                else:
                    # Tracking success
                    marked[i]=0
                    p1 = (int(bbox[i][0]), int(bbox[i][1]))
                    p2 = (int(bbox[i][0] + bbox[i][2]), int(bbox[i][1] + bbox[i][3]))
                    cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)

        prevBbox=[None] * len(tracker)
        prevBbox=bbox

        prevMark=[None] * len(tracker)
        prevMark=marked

        # Display result
        cv2.imshow("Tracking", frame)

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 :
            break
