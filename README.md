# Stride Demo OCR

## Current Version 
4.0



## Installation instructions for dependenceies

## Install python depenecies
```
pip install -r requirements.txt
```

### Instructions to install Tesseract 5.x:

For installing tesseract on Ubuntu 18.X run the following

- Ubuntu
```
Ubuntu
sudo add-apt-repository ppa:alex-p/tesseract-ocr-devel
sudo apt-get update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```


Verify tesseract Installation is up to date by running the following:

*tesseract -v*
Output should look similar to below:
```
tesseract 5.0.0-alpha-820-ge20f
 leptonica-1.78.0
  libgif 5.1.4 : libjpeg 8d (libjpeg-turbo 1.5.2) : libpng 1.6.34 : libtiff 4.0.9 : zlib 1.2.11 : libwebp 0.6.1 : libopenjp2 2.3.0
 Found AVX512BW
 Found AVX512F
 Found AVX2
 Found AVX
 Found FMA
 Found SSE
 Found OpenMP 201511
 Found libarchive 3.2.2 zlib/1.2.11 liblzma/5.2.2 bz2lib/1.0.6 liblz4/1.7.1

```

Please make sure that the tesseract is using 4.x+.Not  3.X. If so, redo installation steps or consult the link in below.

The same applies for leptonica. This has to be 1.78.0 +


Additional supported OS installation isntructions can be found below:
```
https://github.com/tesseract-ocr/tesseract/wiki
```

Download additional tessercat langauges using the script below
```
import requests

lang = {
    'en': 'eng',
    'ar': 'ara',
    'da': 'dan',
    'nl': 'nld',
    'de': 'deu',
    'fr': 'fra',
    'is': 'isl',
    'no': 'nor',
    'pl': 'pol',
    'it': 'ita',
    'es': 'spa',
    'pt': 'por'
}

def download_file(link, file_path, connection_timeout=10):
    try:
        r = requests.get(link, stream = True, timeout=(connection_timeout, 90), verify=False)
        for chunk in r.iter_content(32):
            file_path.write(chunk)
    except:
        try:
            r = requests.get(link, timeout=(
                connection_timeout, 90), verify=False)
            with open(file_path, 'wb+') as destination:
                destination.write(r.content)

        except:
            pass


if __name__ == '__main__':
    lang_input  = input("enter the language code -  ")

    if lang_input in lang:
        link_data = 'https://github.com/tesseract-ocr/tessdata_fast/raw/master/'+lang[lang_input]+'.traineddata'
        print(link_data)
        file_path = "/home/sneha/Documents/Stride/Titus/language_documents/download"
        download_file(link_data, file_path, 50)
```
The language files have to be in the path for your envorinment (dev or demo) which is defined in `constants.py`

- RedHat

Install tesseract 5 from

https://build.opensuse.org/project/show/home:Alexander_Pozdnyakov:tesseract5


### ImageMagick Installation Instructions

Install 'Imagemagick' by running  the following : 
```
apt-get install imagemagick
```
Ensure that Imagemaick has the apporpriate permissions for processing pdf files by doing the following:
You may need sudo permission.
```
nano /etc/Imagemagick-6/policy.xml
```

Add or edit the following entry
```
<policy domain="coder" rights="read|write" pattern="PDF" />
```

## Instructions for using Stride OCR as a Devoloper


Change path to langauge files in `constants.py`
comment out the path that does not apply.


# Solutions for commonly encountered errors.
Q: Compling tesseract from souce or if Tesseract fails to work

Ans: copy *pdf.ttf* in installation_files to */usr/local/share/tessdata/*

Q. Image Magick or "convert " Doesnt work? 

Ans: Modify policy.xml like outlined in the intsallation instructions

Q.cannot find ximgproc error on new production error?

Ans: Uninstall opencv-python and retain opencv-contrib. Ensure only opencv-contrib in installed. 

Q: When running python mange.py runserver you get the following error - "from .cv2 import *ImportError: libSM.so.6:" 

Ans: sudo apt-get install libsm6 libxrender1 libfontconfig1


Q. Question not covered here?

Ans : look at https://github.com/tesseract-ocr/tesseract/wiki/FAQ or https://github.com/tesseract-ocr/tesseract/wiki/FAQ-Old

