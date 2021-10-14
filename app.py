from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import cv2
 

 
app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     

def cartoonify(image):
  #read the image 
  originalmage =  image
  #print(image)  # image is stored in form of numbers
  
  # confirm that image is chosen
  if originalmage is None:
    print("Can not find any image. Choose appropriate file")
    sys.exit()
    
    
  ReSized1 = cv2.resize(originalmage, (960, 540))
  #plt.imshow(ReSized1, cmap='gray')
  
  #converting an image to grayscale
  grayScaleImage = cv2.cvtColor(originalmage, cv2.COLOR_BGR2GRAY)
  ReSized2 = cv2.resize(grayScaleImage, (960, 540))
  #plt.imshow(ReSized2, cmap='gray')
  
  #applying median blur to smoothen an image
  smoothGrayScale = cv2.medianBlur(grayScaleImage, 5)
  ReSized3 = cv2.resize(smoothGrayScale, (960, 540))
  #plt.imshow(ReSized3, cmap='gray')
  
  #retrieving the edges for cartoon effect
  #by using thresholding technique
  getEdge = cv2.adaptiveThreshold(smoothGrayScale, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY, 9, 9)
  ReSized4 = cv2.resize(getEdge, (960, 540))
  #plt.imshow(ReSized4, cmap='gray')
  
  #applying bilateral filter to remove noise 
  #and keep edge sharp as required
  colorImage = cv2.bilateralFilter(originalmage, 9, 300, 300)
  ReSized5 = cv2.resize(colorImage, (960, 540))
  #plt.imshow(ReSized5, cmap='gray')
  
  #masking edged image with our "BEAUTIFY" image
  cartoonImage = cv2.bitwise_and(colorImage, colorImage, mask=getEdge)
  
  ReSized6 = cv2.resize(cartoonImage, (960, 540))
  #plt.imshow(ReSized6, cmap='gray')
  return cartoonImage
 
@app.route('/')    
def home():
    return render_template('index.html') 
 
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url) 
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        originalmage = cv2.imread(UPLOAD_FOLDER+filename) 
        cartoon = cartoonify(originalmage)
        cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], filename), cartoon)
        #print('upload_image filename: ' + filename) 
        return render_template('index.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
 
if __name__ == "__main__":   
    app.run(debug=True)
   
 