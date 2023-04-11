import os
import json
from traceback import *

from slugify import slugify
from kafka import KafkaConsumer, KafkaProducer


# from ocrize import init_ocr_tesseract
# from prepare_document_for_ocr import process_and_ocr_file, pdf_pages_to_pdf
from run import perform_ocr_image_files, perform_ocr

from constants import *
import pytz
from datetime import datetime


def ocr_call(request_data):
    pdf_language = "all"
    # Get filename
    try:
        pdf_splice = bool(int(request_data["pdf_splice"]))
        pdf_language = request_data["lang"]

        """preprocess_options = {}
        for index, key in enumerate(request_data):
            if key not in ["pdf_splice"]:
                continue
            preprocess_options[key] = bool(int(request_data[key]))"""
    except Exception as e:
        print(e)
        return ("Invalid input data")
    input_file_name = request_data["file_name"]
    input_file_extention = input_file_name.split(".")[-1]

    file_name = slugify(input_file_name).split('pdf')[0] + '.' + input_file_extention
    ocr_name = slugify(input_file_name).split('pdf')[0] + "_ocr.pdf"
    
    # Create archive directory
    folder_path = request_data["folder"]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, file_name)
    ocr_path = os.path.join(folder_path, ocr_name)
    doc = request_data["doc"]
    path_to_pdf_pages = request_data["file_path"]
    doc["status"]="ocr_process"
    if(request_data["file_type"]=="image"):
        doc = perform_ocr_image_files(doc, path_to_pdf_pages, ocr_path, pdf_language)
        if("ocr_process"=="completed"):
            proc_complete = datetime.strptime(doc["processing_completed"], '%B %d %Y - %H:%M:%S')
            proc_start = datetime.strptime(doc["processing_started"], '%B %d %Y - %H:%M:%S')
            secs = (proc_complete - proc_start).seconds
        else:
            secs=0
    else:
        doc = perform_ocr( path_to_pdf_pages,
                    doc,
                    ocr_path,
                    folder_path,
                    pdf_language,
                    pdf_splice,)
        if(doc["status"]=="completed"):
            proc_complete = datetime.strptime(doc["processing_completed"], '%B %d %Y - %H:%M:%S')
            proc_start = datetime.strptime(doc["processing_started"], '%B %d %Y - %H:%M:%S')
            secs = (proc_complete - proc_start).seconds
        else:
            secs=0
        
    return_value = {
        "status": doc["status"],
        "result": {"time_taken": secs, "ocr_path": ocr_path, "id":request_data["id"]},
    }
        
    return (return_value)

def kafka_functions_ocr(): 
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda m: json.dumps(m).encode('utf-8'))
    consumer = KafkaConsumer(bootstrap_servers=['localhost:9092'],
                             value_deserializer=lambda m: json.loads(m.decode('ascii')))
    consumer.subscribe(['ocr'])
    while 1:
        for message in consumer:
            if(message.value["doc"]["status"]=="failed"):
                producer.send('status', {"status":"failed"})
                continue
            #request_data = message.value.decode('utf-8')
            print("Received message")
            data = ocr_call(message.value)
            producer.send('status', data)
        producer.flush()

kafka_functions_ocr()