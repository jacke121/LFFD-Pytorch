'''
@Descripttion: This is Aoru Xue's demo,which is only for reference
@version: 
@Author: Aoru Xue
@Date: 2019-09-02 21:08:56
@LastEditors: Aoru Xue
@LastEditTime: 2019-10-01 10:03:36
'''
import cv2
import torch
import os
#from vgg_ssd import build_ssd_model
from model import BasketNet
from torchvision import transforms
#from transforms import *
from PIL import Image
from viz import draw_bounding_boxes
from post_processer import PostProcessor
post_process = PostProcessor()
transform = transforms.Compose([
        transforms.Resize((512,512)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]
    )
# predict_transform = Compose([
#             Resize(300),
#             SubtractMeans([123, 117, 104]),
#             ToTensor()
#         ])
import numpy as np
def center_form_to_corner_form(locations):
    return np.concatenate([locations[..., :2] - locations[..., 2:] / 2,
                      locations[..., :2] + locations[..., 2:] / 2], 1)

def pic_test():
    # img = Image.open("datasets/images/009814.jpg").convert('RGB')
    # image = np.array(img,dtype = np.float32)


    path='datasets/images/'
    files=os.listdir(path)
    net = BasketNet()

    net.load_state_dict(torch.load("./ckpt/61.pth"))
    net.cuda()
    net.eval()
    for file in files:
        image=cv2.imread(path+file)
        height, width, _ = image.shape
        img = transform(Image.fromarray(image))
        img = img.unsqueeze(0)
        img = img.cuda()
        with torch.no_grad():
            pred_confidence,pred_bbox = net(img)

            output = post_process(pred_confidence,pred_bbox, width=width, height=height)[0]

            boxes, labels, scores = [o.to("cpu").numpy() for o in output]
            print(boxes)
            print(scores)
            drawn_image = draw_bounding_boxes(image, boxes, labels, scores, ("__background__","basketball","volleyball")).astype(np.uint8)

            cv2.imshow("img", drawn_image)
            # Image.fromarray(drawn_image).save("./a.jpg") 
            key = cv2.waitKey()
            if key == ord("q"):
                break

        # Image.fromarray(drawn_image).save("./a.jpg")

def cap_test():
    # cap = cv.VideoCapture("./test.mp4")
    cap = cv2.VideoCapture(0)
    net = BasketNet()
    
    net.load_state_dict(torch.load("./ckpt/61.pth",map_location='cpu'))
    net.cuda()
    net.eval()
    while True:
        ret,frame = cap.read()
        if not ret:
            break
        height,width,_ = frame.shape
        cv_img = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv_img)
        img = transform(img)
        img = img.unsqueeze(0)
        img = img.cuda()

        with torch.no_grad():
            pred_confidence,pred_bbox = net(img)
            #print(pred_confidence)
            
            output = post_process(pred_confidence,pred_bbox, width=width, height=height)[0]
            
            boxes, labels, scores = [o.to("cpu").numpy() for o in output]
            if len(labels)>0:
                print(boxes)
            drawn_image = draw_bounding_boxes(frame, boxes, labels, scores, ("__background__","basketball","volleyball")).astype(np.uint8)
            cv2.imshow("img",drawn_image)
            #Image.fromarray(drawn_image).save("./a.jpg")
        key = cv2.waitKey(1)
        if key == ord("q"):
            break
    cv2.destroyAllWindows()
    cap.release()
if __name__ == "__main__":
    # cap_test()
    pic_test()