import streamlit as st
import requests
import io
from PIL import Image,ImageFilter
import numpy as np
def filter_vintage(img):
    arr = np.array(img,dtype=np.float32)
    arr[:,:,0]=np.clip(arr[:,:,0]*1.1+20,0,255)
    arr[:,:,1]=np.clip(arr[:,:,1]*0.9+10,0,255)
    arr[:,:,2]=np.clip(arr[:,:,2]*0.8,0,255)
    return Image.fromarray(arr.astype(np.uint8))
def filter_cinema(img):
    arr = np.array(img,dtype=np.float32)
    arr[:,:,0]=np.clip(arr[:,:,0]*1.9+20,0,255)
    arr[:,:,2]=np.clip(arr[:,:,2]*1.15,0,255)
    return Image.fromarray(arr.astype(np.uint8))
def filter_warm(img):
    arr = np.array(img,dtype=np.float32)
    arr[:,:,0]=np.clip(arr[:,:,0]+40,0,255)
    arr[:,:,2]=np.clip(arr[:,:,2]-40,0,255)
    return Image.fromarray(arr.astype(np.uint8))
def filter_bw (img):
    return img.convert ("L").convert ("RGB")
def filter_sharp (img):
    return img.filter (ImageFilter.SHARPEN)
filters={
    "NO filter":None,
    "vintage":filter_vintage,
    "b&w":filter_bw,
    "sharp":filter_sharp,
    "cinema":filter_cinema,
    "warm":filter_warm,
}
    


    
st.title("image filter")
api_key = st.text_input ("Enter your api from remve.bg", type="password")
image_file = st.file_uploader ("choose your image",type=["jpg","png","jpeg"])

bg_file =st.file_uploader ("choose your plac", type = ["jpg" , "png" , "jpeg"])

if image_file and bg_file and api_key :
    img=Image.open(image_file).convert("RGBA")
    bg_img = Image.open(bg_file).convert("RGBA")
    st.subheader("original image")
    col1 ,col2 = st.columns(2)
    col1.image(img)
    col2.image(bg_img)
    with st.spinner ("removing bg ..."):
       
        image_file .seek (0)
        response = requests.post (
            "https://api.remove.bg/v1.0/removebg" ,
            files= {"image_file" : image_file} ,
            data= {"size" : "auto"} ,
            headers= {"X-APi-key":api_key})
    if response.status_code == 200 :
        person_no_bg = Image.open(io.BytesIO(response.content)).convert ("RGBA")
        st.subheader("size and position")
        scale =st.slider("person size",10,100,50)
        pos_x = st.slider("person position x",0,100,50)
        pos_y=st.slider("person position y",0,100,50)
        bg_w , bg_h =bg_img.size
        new_h =int(bg_h * scale /100)
        ratio =new_h/person_no_bg.size[1]
        new_w = int(person_no_bg.size[0]*ratio)
        person_resized = person_no_bg.resize((new_w,new_h),Image.LANCZOS)
        X = int ((bg_w - new_w) * pos_x / 100)
        y= int ((bg_h - new_h) * pos_y / 100)
        result = bg_img.copy ()
        result.paste (person_resized , (X,y), person_resized)

        st.subheader("choose filter") 
        choice =st.radio("",list(filters.keys()),horizontal=True)
        filtered = result.convert("RGB")
        if filters [choice]:
            filtered = filters[choice] (filtered)
        st.subheader ("filterd image")
        st.image (filtered)

        d_img = io.BytesIO()
        filtered.save(d_img,format="PNG")
        d_img.seek(0)
        st.download_button("download",d_img,file_name="image.png",mime="image/png")
    else:
        st.error(response.status_code)
else:
    st.error("enter the api key")
