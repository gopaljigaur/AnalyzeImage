# AnalyzeImage

This is an Image Analyzing API that uses of **Microsoft Computer Vision API** to perform various tasks on the image. 
These include:
* Detecting the faces, gender and age of people present in the image
* Providing a suggested title to the image
* Generating tags related to the image

Please note that this API requires the image to be sent in a **base64** format via POST request to [http://gopaljigaur.ap-south-1.elasticbeanstalk.com/test](http://gopaljigaur.ap-south-1.elasticbeanstalk.com/test). You will receive a json response containing these tags:
* `Image`
* `Image_Title` 
* `Image_Tags`

The received image will also be encoded in **base64** format and you need to decode it to view the original image.

NOTICE: It's currently defunct. Will resume services shortly