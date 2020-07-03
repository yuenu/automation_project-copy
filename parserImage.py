from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'

def idenitfy_img(img):
	# Thresh_binary
	def convert_img(img,threshold):
		img = img.convert("L")
		pixels = img.load()
		for x in range(img.width): 
			for y in range(img.height): 
				if pixels[x, y] > threshold: 
					pixels[x, y] = 255
				else:
					pixels[x, y] = 0
		return img

	# Convert img to gray, direct tesseract and get value to fourth digits
	captcha = Image.open(img)
	Gray_captcha = captcha.convert('L')
	result = pytesseract.image_to_string(Gray_captcha, config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')[:4]
	if len(result) > 3:
		pass
	# If not get 4 digits, then change threshold to get cleand img until idenitfy 4 digits
	else :
		threshold = 170
		thresh = convert_img(captcha, threshold)
		result = pytesseract.image_to_string(thresh, config='--psm 13 --oem 1 -c tessedit_char_whitelist=0123456789')          
		for i in range(80):
			if len(result) < 4:
				threshold = threshold-1
				thresh = convert_img(captcha, threshold)
				result = pytesseract.image_to_string(thresh, config='--psm 13 --oem 1 -c tessedit_char_whitelist=0123456789')[:4]
	return result
