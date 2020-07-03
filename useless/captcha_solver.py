import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'

j = input("input Whitch img want Identify Number:")
captchap = f'./captcha/{j}.png'


def idenitfy_img(captcha_path):

    def convert_img(img,threshold):  
        #二值化
        img = img.convert("L") 
        pixels = img.load() 
        for x in range(img.width): 
            for y in range(img.height): 
                if pixels[x, y] > threshold: 
                    pixels[x, y] = 255      
                else: 
                    pixels[x, y] = 0
        return img


    captcha = Image.open(captcha_path)

    Gray_captcha = captcha.convert('L')

    result = pytesseract.image_to_string(Gray_captcha, config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')[:4]
    
    if len(result) > 3:
        pass
        
    else:
        threshold = 170
        thresh = convert_img(captcha, threshold)
        result = pytesseract.image_to_string(thresh, config='--psm 13 --oem 1 -c tessedit_char_whitelist=0123456789')
        
        for i in range(100):
            if len(result) < 4:
                threshold = threshold-1
                thresh = convert_img(captcha, threshold)
                result = pytesseract.image_to_string(thresh, config='--psm 13 --oem 1 -c tessedit_char_whitelist=0123456789')[:4]
                
    return print(result)


idenitfy_img(captchap)