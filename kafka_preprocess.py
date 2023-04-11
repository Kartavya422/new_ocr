import os
import random
import string
import json
from traceback import *

from slugify import slugify
from kafka import KafkaConsumer, KafkaProducer


from settings import ARCHIVE_DIR

# from ocrize import init_ocr_tesseract
# from prepare_document_for_ocr import process_and_ocr_file, pdf_pages_to_pdf
from run import perform_ocr_image_files, perform_ocr_container_files, perform_ocr

from constants import *



def preprocess_call(request_data):
    try:
            preprocess = bool(int(request_data["preprocess"]))
            pdf_splice = bool(int(request_data["pdf_splice"]))
            pdf_language = request_data["lang"]

            preprocess_options = {}
            for index, key in enumerate(request_data):
                if key in ["lang","file_path", "id"]:
                    continue
                preprocess_options[key] = bool(int(request_data[key]))
                print (key,request_data[key])
            print (preprocess_options)
    except Exception as e:
        print(e)
        return ({"doc":{"status":"failed"},"message":"Invalid input data"})
    try:
        file_path = request_data["file_path"]
        file =  open(file_path, "rb")
    except Exception as err:
        print(err)
        return ({"doc":{"status":"failed"},"message":"Document must be uploaded with key `file`"})
    input_file_name = file.name
    input_file_extention = input_file_name.split(".")[-1]

    file_name = slugify(input_file_name).split('pdf')[0] + '.' + input_file_extention
    ocr_name = slugify(input_file_name).split('pdf')[0] + "_ocr.pdf"

    # Check if file extention is supported by the Stride OCR
    if input_file_extention.lower() not in CONTAINER_FILES + IMAGE_FILES:
        return ({"doc":{"status":"failed"},"message":"Not a suported file format"})

    # Create archive directory
    random_string = "".join(random.choice(string.ascii_uppercase) for _ in range(8))
    folder_path = os.path.join(ARCHIVE_DIR, random_string)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path, file_name)
    ocr_path = os.path.join(folder_path, ocr_name)
    # Move input file to archive folder



    with open(file_path, "wb+") as destination:
        destination.write(file.read())
        # for chunk in file.chunks():
        #     destination.write(chunk)

    doc = {"folder_name":random_string,
        "input_file_name":file_name,
        "output_file_name":ocr_name,
    }
    # If container format Pass it to the preprocessing script
    # eg - pdf, tif
    if input_file_extention.lower() in CONTAINER_FILES:
        path,doc = perform_ocr_container_files(
                doc,
                file_path,
                ocr_path,
                folder_path,
                pdf_language,
                preprocess,
                pdf_splice,
                preprocess_options,
            )
        
        ret_data = {"doc": doc, "file_path":path,  "folder":folder_path, 
                    "file_name":input_file_name,"file_type":"document","lang":pdf_language,"pdf_splice":pdf_splice, "id":request_data["id"]}
        return (ret_data)
    
    else:
        doc["status"]="ocr"
        ret_data = {"doc": doc, "file_path":file_path,"folder":folder_path, 
                    "file_name":input_file_name,"file_type":"image","lang":pdf_language,"pdf_splice":False, "id":request_data["id"]}
        return (ret_data)
    
def kafka_functions_preprocess():
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda m: json.dumps(m).encode('utf-8'))
    consumer = KafkaConsumer(bootstrap_servers=['localhost:9092'],
                             value_deserializer=lambda m: json.loads(m.decode('ascii')))
    consumer.subscribe(['preprocess'])
    while 1:
        print("debug")
        for message in consumer:
            #request_data = message.value.decode('utf-8')
            print(message)
            data = preprocess_call(message.value)
            print(data)
            producer.send('ocr', data)
        producer.flush()
    # data = preprocess_call({"preprocess": 1,
    #     "deskew": 0,
    #     "rotate": 1,
    #     "luin_fix":0,
    #     "denoise": 1,
    #     "enable_filers": 1,
    #     "enable_superres": 1,
    #     "pdf_splice": 0,
    #     "lang": "en",
    #     "file_path":"/home/kartavya/Stride/arabic1.pdf"})
    # print(data)

if __name__ == "__main__":
    print("aaa")
    kafka_functions_preprocess()