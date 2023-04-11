import os
import logging
import subprocess
from traceback import format_exc
from threading import Timer
import signal
from constants import *

logger = logging.getLogger("ocr")



def call_command(cmd_tesseact, timeout_sec):
    print (timeout_sec) 
    timeout_sec =  int(timeout_sec)
    logger.debug(cmd_tesseact)

    proc = subprocess.Popen(
        cmd_tesseact,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        preexec_fn=os.setsid,
    )

    def kill_proc():
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

    timer = Timer(timeout_sec, kill_proc)
    timer.start()
    stdout, stderr = proc.communicate()
    timer.cancel()
    return stdout, stderr


def init_ocr_tesseract(file_path, ocr_path, timeout=15, language_mode="all", is_image_input = False):

    """
        Description :   This function calls tesseract and ocrizes and returns a single pdf file
                            for an input file in the following formats :
                            (TIF, JPG, JPEG, PDF)

        Input       :   Path to the input file       (String)
                        Path path to the output file (String) 
                        Upper bound  time in minutes to spend on each file (int)
                        Language of the ocr backend model (string)
                        Flag to denote image input (Bool)


        Return      :   flag that denotes process sucess   (Bool)

        Author      :   Titus@stride
    """
    # Output to avoid schema errors
    ocr_file_noext = ocr_path.replace(".pdf", "")
    cmd_tesseact = ""
    
    # Tessercat Parameters ( python is not importing constants properly)
    # Dev
    TESS_DATA_DIR = "/opt/homebrew/Cellar/tesseract/5.3.1/share/tessdata/"

    # Prod
    # TESS_DATA_DIR = "/home/stride/.local/share/tessdata"
    TESS_CMD_HEAD = "tesseract "
    TESS_PARMS = " --psm 1 --oem 1 pdf"
    TESS_PARMS = TESS_PARMS + " -c tessedit_do_invert=0"
    TESS_PARMS_OPT = " --dpi 300"
    TESS_DATA_DIR_CMD =  " --tessdata-dir  "


    if is_image_input == False:
        TESS_PARMS = TESS_PARMS_OPT + TESS_PARMS    

    # formatting I/O paths to avoid string errors.
    file_path = '"{}"'.format(file_path)
    ocr_file_noext = '"{}"'.format(ocr_file_noext)
    TESS_DATA_DIR = '"{}"'.format(TESS_DATA_DIR)

    # command calls for tesseact and permissions

    if language_mode == "all":
        cmd_tesseact = (
            TESS_CMD_HEAD + file_path + " " + ocr_file_noext + TESS_PARMS
        )
    language_mode = language_mode.split('+')
    check =  all(item in OCR_SUPPORTED_LANGS.keys() for item in language_mode)
    language_tess_final = ' -l '
    if check:

        # get langauge code for tess from iso dict
        for language in language_mode:
            language_tess = OCR_SUPPORTED_LANGS.get(language)
            # if langauge not in dict. default to normal ocr
            if language_tess == None:
                language_tess = ""
            elif language_tess_final==' -l ':
                language_tess_final =language_tess_final + language_tess
            else:
                language_tess_final =language_tess_final + '+' + language_tess
        cmd_tesseact = (
            TESS_CMD_HEAD
            + file_path
            + " "
            + ocr_file_noext
            + TESS_DATA_DIR_CMD
            + TESS_DATA_DIR
            + language_tess_final
            + TESS_PARMS
        )
    # print(cmd_tesseact)

    count = 0
    while count < 3:
        stdout, stderr = call_command(cmd_tesseact, timeout)
        
        if os.path.exists(ocr_path):
            logger.debug("OCR successful: " + ocr_path)
            break
        count += 1
    # print(stdout, stderr)
    if os.path.exists(ocr_path):
        return True, None
    logger.error("Failed to OCRize: %s - %s" % (stdout, stderr))
    return False, None

if __name__ == "__main__":

    file_path = "./test_files/t1.tif"
    ocr_path =  "./test_files/t1_ocr"
    init_ocr_tesseract(file_path, ocr_path, timeout=15, language_mode="all", is_image_input = False)

    pass
