import math
import re
import subprocess
import time
from enum import Enum
import io
import shutil
import sys
import os
import datetime
from PIL import Image
import fitz
# from logger import Logger
from difflib import SequenceMatcher
import pandas as pd
from tkinter import messagebox
try:
    from google.cloud import vision
except:
    subprocess.run(["pip install --upgrade google-cloud-vision"])
    from google.cloud import vision

######################################################
######################################################
import logging

from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, path: str = ''):
        if not path:
            import os
            path = os.path.abspath(os.path.dirname(__file__))

        current_time = datetime.now()
        formatted_current_time = datetime.strftime(current_time, '%d_%m-%H_%M')

        logging_handler = RotatingFileHandler(f'{path}/{formatted_current_time}.log',
                                             maxBytes=1000000,
                                             backupCount=0,
                                             encoding='utf-8')

        logging.basicConfig(handlers=[logging_handler],
                            format='%(asctime)s __%(levelname)s__ __%(name)s__ %(message)s',
                            datefmt='%m-%d-%Y %H:%M:%S',
                            level=logging.INFO)


    def get_logger(self, name: str = ''):
        return logging.getLogger(name)

######################################################
######################################################
#               VARIABLES
input_folder_path = ''
output_folder_path = ''

PATH = os.path.abspath(os.path.dirname(__file__))
#
if os.path.isfile(os.path.join(PATH,'database','processed.csv')):
    pass
else:
    database = pd.DataFrame(columns=['input_name','output_name','ocr_data','processed'])
    database.to_csv(os.path.join(PATH,'database','processed.csv'),index=False)
#
logger_obj = Logger(os.path.join(PATH,'logs'))
logger = logger_obj.get_logger()
#
metada_ocr = []
#
class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5
#
def set_env_var():
    creds_path = os.path.join(PATH,'ocr-python-vision_key.json')
    # a = os.path.join(PATH,'ocr-python-vision_key.json')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(creds_path)
    logger.info(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
#
def similar(table, miner):
    return SequenceMatcher(None, table, miner).ratio()

######################################################
#               READ INPUT
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)


   return "%s %s" % (s, size_name[i])

def check_existance_in_database(file_name):
    dc_for_name_check = pd.read_csv(os.path.join(PATH,'database','processed.csv'))
    for ind,row in dc_for_name_check.iterrows():
        if file_name.endswith('.pdf'):
            if file_name.replace('.pdf','') in str(dc_for_name_check.loc[ind,'input_name']):
                return True
        if  str(dc_for_name_check.loc[ind,'input_name']) == file_name:
            return True
    return False


def extract_images_():
    logger.info('Extracting Images')
    for folder in os.listdir(input_folder_path):
        if os.path.isdir(os.path.join(input_folder_path,folder)):
            for p in os.listdir(os.path.join(input_folder_path,folder)):
                if check_existance_in_database(p):
                    print('---- Exists --',p)
                    continue
                path = os.path.join(input_folder_path,folder,p)
                if path.endswith('.jpg') or path.endswith('.JPG') or path.endswith('.png') or path.endswith('.PNG'):
                    img = Image.open(path)
                    img.save(f'{output_folder_path}/{p}')
                    size_in_mb = convert_size(os.path.getsize(f'{output_folder_path}/{p}'))
                    if 'MB' in size_in_mb:
                        if float(size_in_mb.replace('MB', '')) > 2:
                            logger.info(f'{float(size_in_mb.replace("MB", "")) }MB')
                            height = int(img.size[0]) - (int(img.size[0]) * 0.925)
                            width = int(img.size[1]) - (int(img.size[1]) * 0.925)
                            if width > 1050 or height > 1050:
                                height = 1000
                                width = 1000
                            logger.info(f'Original Dimensions {img.size}')
                            logger.info(f'Converted to: {height}{ width}')
                            img.thumbnail(size=(height, width))
                            img.save(f'{output_folder_path}/{p}')
                    if 'GB' in size_in_mb:
                        os.remove(f'{output_folder_path}/{p}')
                        continue
                    continue
                # pdf process
                if '.pdf' in path:
                    doc = fitz.open(path)
                    for page in doc:
                        # logger.info(page.mediabox)
                        dpi = 300
                        zoom = dpi / 72
                        magnify = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=magnify)
                        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
                        img.save(f'{output_folder_path}/{p.replace(".pdf","")}-page{page.number}.jpg')
                        size_in_mb=convert_size(os.path.getsize(f'{output_folder_path}/{p.replace(".pdf","")}-page{page.number}.jpg'))
                        if 'MB' in size_in_mb:
                            if float(size_in_mb.replace('MB','')) > 2:
                                logger.info(f"{float(size_in_mb.replace('MB',''))}'MB'")
                                height = int(img.size[0])-(int(img.size[0]) * 0.925)
                                width = int(img.size[1])-(int(img.size[1]) * 0.925)
                                if width > 1050 or height > 1050:
                                    height = 1000
                                    width = 1000
                                logger.info(f'Original Dimensions{img.size}')
                                logger.info(f'Converted to: {height} {width}')
                                img.thumbnail(size=(height,width))
                                img.save(f'{output_folder_path}/{p.replace(".pdf","")}-page{page.number}.jpg')
                        if 'GB'in size_in_mb:
                            os.remove(f'{output_folder_path}/page{page.number}.jpg')
                        logger.info(f'Converting to png page: {page.number}')
                        logger.info('###############################')
    pass
######################################################
#                   SCANNING
def write_to_db(input_name,output_name,ocr_data,processed):
    data = {
        'input_name':[input_name],
        'output_name':[output_name],
        'ocr_data':[ocr_data],
        'processed':[processed],
    }
    pd.concat([pd.read_csv(os.path.join(PATH,'database','processed.csv')),pd.DataFrame.from_dict(data)]).to_csv(os.path.join(PATH,'database','processed.csv'),index=False)
    pass

def check_for_duplicate(ocr_data):
    database_to_check = pd.read_csv(os.path.join(PATH,'database','processed.csv'))
    for ind, row in database_to_check.iterrows():
        if similar(str(database_to_check.loc[ind,'ocr_data']),ocr_data) > 0.97:
            return True
    return False
    pass

def process_image(path,old_name):
    try:
        text_extracted = scan(path,FeatureType.WORD)
        image_renamed = detect_id(text_extracted)
        print(text_extracted)
        print(image_renamed)
        if image_renamed != None:
            if check_for_duplicate(str(text_extracted)) == True:
                print('DUPLICATED')
                return 'duplicate@@!!@@'
            # convert to pdf here
            if 'is_doc' in image_renamed:
                logger.info(f'is doc {path}')
                print('detected is doc')
                convert_to_pdf(path,image_renamed,old_name,text_extracted)
                return image_renamed.replace('.jpg','.pdf')
            write_to_db(old_name,image_renamed,text_extracted,True)
            return image_renamed
        for i in range(4):
            logger.info(f'RETRYING {i}: {path}')
            if i > 0:
                img = Image.open(path)
                img = img.rotate(90)
                img.save(path)
                logger.info(f'roteted {i}')
            text_extracted = scan(path, FeatureType.WORD)
            image_renamed = detect_id(text_extracted)
            if image_renamed != None:
                if 'is_doc' in image_renamed:
                    convert_to_pdf(path, image_renamed, old_name, text_extracted)
                    return image_renamed.replace('.jpg', '.pdf')
                write_to_db(old_name, image_renamed, text_extracted, True)
                return image_renamed
        return None
    except Exception as ee:
        logger.info(f'except in "process_image" func ERROR: {str(ee)}')
        pass
    return None
#
def scan(path,feature):
    bounds = []
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    texts = response.text_annotations
    data = []
    for text in texts:
        data.append(text.description)
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    document = response.full_text_annotation
    for page in document.pages:
        for block in page.blocks:
            block_text = []
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        block_text.append(symbol.text)
                    block_text.append(' ')
                block_text.append('@!!@')
            bounds.append(''.join(block_text))
    return [data,bounds]
#
def detect_id(data):
    blocks = data[1]
    print(blocks)
    data = data[0]
    date = ''
    name = ''
    logger.info(len(blocks))
    if len(blocks) > 15:
        name = 'is_doc'
    if date == '':
        try:
            id = detect_id_vr(blocks)
            if id != None:
                logger.info('V1')
                return f'{id}-{name}-{date}.jpg'
        except Exception as e:
            pass

    if date == '':
        for index, el_ in enumerate(data):
            if str(el_).replace('\n','').replace('  ','').isdigit():
                if len(str(el_).replace('\n','').replace('  ','')) == 5 or len(str(el_).replace('\n','').replace('  ','')) == 6:
                    id = str(el_).replace('\n','').replace(' ','')
                    for f in os.listdir('../../output'):
                        if '.jpg' in str(f):
                            continue
                        if id == str(f):
                            logger.info(f"Founded by existing folder: {id} {date}")
                            logger.info('V3')
                            return f'{id}-{name}-{date}.jpg'

    if date == '':
        try:
            id = detect_id_v2(blocks)
            if id != None and str(id).isdigit() and id != '':
                logger.info('V4')
                return f'{id}-{name}-{date}.jpg'
        except Exception as e:
            pass
    return None
#
def detect_id_vr(blocks):
    for ind_,block_ in enumerate(blocks):
        for possible_id_ in str(block_).replace('@!!@', '').split(' '):
            if str(possible_id_).isdigit():
                if len(str(possible_id_)) == 4:
                    if re.search('\d\d\d\d[-?\s?]\d\d[-?\s?]\d\d', str(block_)) != None:
                        if str(possible_id_) in str(re.search('\d\d\d\d[-?\s?]\d\d[-?\s?]\d\d', str(block_))):
                            continue
                        logger.info('With date 4 digit')
                        metada_ocr.append(block_)
                        return possible_id_
                    if re.search('\d\d\d\d\d?\s\s?[A-Z]+\s\s?', str(block_)) != None:
                        if re.search('\d\d\d\d?[-?\s?]\d\d[-?\s?]\d\d', str(block_)) != None:
                            logger.info('With date 4 digit UPPER')
                            metada_ocr.append(block_)
                            return possible_id_
                if len(str(possible_id_)) == 5:
                    if re.search('\d\d\d\d[-?\s?]\d\d[-?\s?]\d\d', str(block_)) != None:
                        logger.info('With date')
                        metada_ocr.append(block_)
                        return possible_id_
                    if 'patient label' in str(block_).lower():
                        metada_ocr.append(block_)
                        return possible_id_
                    if re.search('\d\d\d\d\d?\s\s?[A-Z]+\s\s?', str(block_)) != None:
                        if re.search('\d\d\d\d?[-?\s?]\d\d[-?\s?]\d\d', str(block_)) != None:
                            logger.info('With date and UPPER')
                            metada_ocr.append(block_)
                            return possible_id_
                if len(str(possible_id_)) == 6:
                    if re.search('\d\d\d\d\d\d\s\s?[A-Z]+\s\s?,?\s\s?()[A-Z]+\s\s?\d+\s', str(block_)) != None:
                        logger.info('Six figures Long founded')
                        metada_ocr.append(block_)
                        return possible_id_
                    if re.search('\d\d\d\d\d\d\s\s?[A-Z]+\s\s?,?\s\s?(\d+)?([A-Z]+)?\s\s?', str(block_.replace('@!!@', ''))) != None:
                        logger.info('Six figures Long founded')
                        metada_ocr.append(block_)
                        return possible_id_
#
def detect_id_v2(blocks):
    possible_id_in_full_page = []
    for block_ in blocks:
        for possible_id_ in str(block_).replace('@!!@','').split(' '):
            if str(possible_id_).isdigit():
                if len(str(possible_id_)) == 5:
                    possible_id_in_full_page.append(possible_id_)
    if len(possible_id_in_full_page) == 1:
        return possible_id_in_full_page[0]
    if len(possible_id_in_full_page) == 0:
        return ''
    logger.info('possible id"s in full page',possible_id_in_full_page)
    more_than_one_id_possible= []
    for id_possible in possible_id_in_full_page:
        for block in blocks:
            count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(id_possible), block))
            if count == 0:
                continue
            if count == 1:
                logger.info(f'one 5 digit number in: {block}')
                year = ''
                month = ''
                day = ''
                #check if this block includes any date
                for possible_date in str(block).replace('-',' ').split(' '):
                    logger.info(possible_date)
                    if str(possible_date).isdigit():
                        if len(str(possible_date)) == 4:
                            if int(possible_date)> 1100 and int(possible_date) < 2023:
                                year = possible_date
                                continue
                        if len(str(possible_date)) == 2:
                            if month == '':
                                if int(possible_date) > 0 and int(possible_date) < 13:
                                    logger.info('month')
                                    month = possible_date
                                    continue
                        if len(str(possible_date)) == 2:
                            if int(possible_date) > 0 and int(possible_date) < 32:
                                logger.info('day')
                                day = possible_date
                                continue
                if year != '':
                    if month != '' and day != '' :
                        logger.info(f'returning by date more than one digits in one block {year} {month} {day}')
                        return id_possible
                    more_than_one_id_possible.append(id_possible)

                if month != '' and day != '':
                    more_than_one_id_possible.append(id_possible)
                logger.info(f"Date items founded  in this block: {year} ^^ {month} ^^ {day}")
                logger.info('###############################################')
            if count >= 2:
                #now whe have two possible id's, i need to check for and number with 5 digits that is nearest date
                date_items = []
                #check if this block includes any date
                possible_id_among_its_concurrents_in_block = ''
                for index_in ,possible_date in enumerate(str(block).replace('-',' ').split(' ')):
                    if str(possible_date).isdigit():
                        if len(str(possible_date)) == 5:
                            possible_id_among_its_concurrents_in_block = str(possible_date)
                        if len(str(possible_date)) == 4:
                            if int(possible_date)> 1100 and int(possible_date) < 2023:
                                date_items.append({'year':index_in})
                                if len(date_items) > 0:
                                    return possible_id_among_its_concurrents_in_block
                        if len(str(possible_date)) == 2:
                            if int(possible_date) > 0 and int(possible_date) < 13:
                                date_items.append({'month':index_in})
                                if len(date_items) >= 1:
                                    return possible_id_among_its_concurrents_in_block
                        if len(str(possible_date)) == 2:
                            if int(possible_date) > 0 and int(possible_date) < 32:
                                date_items.append({'day':index_in})
                                if len(date_items) >= 0:
                                    return possible_id_among_its_concurrents_in_block
#
def convert_to_pdf(path,new_name,old_name,ocr_data):
    new_name_pdf = new_name.replace(f"{str(str('.') + str(new_name.split('.')[-1]))}", '.pdf').replace('is_doc','')
    print('newname_to_pdf --- ',new_name_pdf)
    # new_name_pdf = new_name.replace('.jpg','.pdf').replace('is_doc','')
    image_1 = Image.open(path)
    im_1 = image_1.convert('RGB')
    #check if the file with name id exists
    logger.info(new_name_pdf)
    if os.path.exists(f"{output_folder_path}/{new_name_pdf}"):
        logger.info('existing')
        c = 0
        while True:
            c += 1
            try:
                new_name_index = new_name_pdf.replace('.pdf', '') + f'({c})' + '.pdf'
                logger.info(f'Name Changed to:{ new_name_index}')
                if os.path.exists(f'{output_folder_path}\\{new_name_index}'):
                    continue
                new_name_pdf = new_name_index
                break
            except:
                continue
    write_to_db(old_name, new_name_pdf, ocr_data, True)
    try:
        im_1.save(os.path.join(output_folder_path,new_name_pdf))
        print('SAVED ------',new_name_pdf)
    except Exception as e:
        print(str(e))
        print('####!!!!@#######')

    pass
#
def remove_duplicates_by_ocr_scan():
    #this func will take place to "process image"
    #the last element of the "metadata_ocr" is the element photo that i'm looking if it is similar to another photo.
    #so i will comparing the last info with all previous infos, and if it is the same with another photo then just return None with "process image" function, and "organize photos"function will not process it further.
    #use difflib to match the similarities, with  an index of higher than 0.9
    #TODO this function should read the local database that saves all ocr data for each processed file and find if it exist, if yes, then do not process it
    #TODO with that being said, each ocr data should be saved into that database
    current_photo = metada_ocr[-1]
    if len(metada_ocr) > 2:
        logger.info('in duplicate checking')
        logger.info(metada_ocr[0:-1])
        logger.info(current_photo)
        for p in metada_ocr[0:-1]:
            if similar(str(current_photo),str(p)) >= 0.9:
                # print('similar-----')
                # print(current_photo)
                # print(p)
                metada_ocr.pop(-1)
                return True
    if len(metada_ocr) == 2:
        if similar(str(current_photo), str(metada_ocr[0])) >= 0.9:
            # print('similar-----')
            # print(current_photo)
            # print(metada_ocr[0])
            metada_ocr.pop(-1)
            return True
#########################################################
#               ORGANIZE

def organize_images():
    logger.info('organising photos')
    photos = os.listdir(output_folder_path)
    logger.info(f'Total: {len(photos)}')
    #rename photos
    for img in photos:
        if not '.jpg' in  img.lower() and not '.png' in img.lower() and not '.JPG' in  img.lower() and not '.jpeg' in  img.lower():
        # if not img.endswith('.jpg') or not img.endswith('.JPG') or not img.endswith('.png') or not img.endswith('.PNG'):
            logger.info(f'continued {img}')
            continue
        logger.info(f'Processing: {str(img)}')
        new_name = process_image(os.path.join(output_folder_path,img),img)
        logger.info(f'new Name: {new_name}')
        if new_name != None:
            if 'duplicate@@!!@@' in new_name:
                # print('removing',img)
                os.remove(f'{output_folder_path}/{img}')
                continue
            try:
                logger.info(new_name)
                #check if new_name war ends with .pdf and if so do not rename image,delete it since the image is a pdf and it  has  already been saved
                if new_name.endswith('.pdf'):
                    logger.info(f'removing {img}')
                    os.remove(f'{output_folder_path}/{img}')
                else:
                    os.rename(f'{output_folder_path}/{img}', f'{output_folder_path}/{new_name}')
            except Exception as e:
                if 'already exists' in str(e):
                    c = 0
                    while True:
                        c+=1
                        try:
                           new_name_index = new_name.replace('.jpg','')+f'({c})'+'.jpg'
                           logger.info(f'Name Changed to: {new_name_index}')
                           os.rename(f'{output_folder_path}/{img}', f'{output_folder_path}/{new_name_index}')
                           break
                        except:
                            continue
        else:
            write_to_db(img, img,f'{img[-1:-4]}-not-founded', True)
            if os.path.exists(os.path.join(output_folder_path,'unresolved')):
                try:
                    shutil.move(os.path.join(output_folder_path,img), os.path.join(output_folder_path,'unresolved',img))
                except:
                    #means that this image name exists in unresolved, just delete
                    os.remove(os.path.join(output_folder_path,img))
                    pass
            else:
                os.mkdir(os.path.join(output_folder_path,'unresolved'))
                try:
                    shutil.move(os.path.join(output_folder_path,img), os.path.join(output_folder_path,'unresolved',img))
                except:
                    #means that this image name exists in unresolved, just delete
                    os.remove(os.path.join(output_folder_path,img))
                    pass
            pass
        logger.info('####################################')
    #insert into folders accordingly
    for el in os.listdir(output_folder_path):
        if el.endswith('.jpg') or el.endswith('.pdf'):
            id = el.split("-")[0]
            try:
                os.mkdir(f'{output_folder_path}/{id}')
            except Exception as e:
                try:
                    os.mkdir(f'{output_folder_path}/unresolved')
                except:
                    pass
            try:
                if os.path.exists(f'{output_folder_path}/{id}/{el}'):
                    logger.info('exists in id folder')
                    logger.info(f'{output_folder_path}/{id}/{el}')
                    c = 0
                    while True:
                        c+=1
                        try:
                            if el.endswith('.jpg'):
                                #check if path has (1) and remove it sot it wouldn't become (1) (1).jpg
                                if re.search('\(\d\d?\d?\d?\d?\)', el) != None:
                                    logger.info(re.search('\(\d\d?\d?\d?\d?\)', el).group())
                                    new_name_index = el.replace(re.search('\(\d\d?\d?\d?\d?\)',el).group(),'').replace('.jpg','')+f'({c})'+'.jpg'
                                else:
                                    new_name_index = el.replace('.jpg','')+f'({c})'+'.jpg'

                            if el.endswith('.pdf'):
                                if re.search('\(\d\d?\d?\d?\d?\)', el) != None:
                                    logger.info(re.search('\(\d\d?\d?\d?\d?\)', el).group())
                                    new_name_index = el.replace(re.search('\(\d\d?\d?\d?\d?\)',el).group(),'').replace('.pdf','')+f'({c})'+'.pdf'
                                else:
                                    new_name_index = el.replace('.pdf', '') + f'({c})' + '.pdf'
                            logger.info(f'Name Changed to: {new_name_index}')
                            if os.path.exists(f'{output_folder_path}/{id}/{new_name_index}'):
                                continue
                            os.rename(f'{output_folder_path}/{el}', f'{output_folder_path}/{new_name_index}')
                            shutil.move(f'{output_folder_path}/{new_name_index    }', f'{output_folder_path}/{id}/{new_name_index}')
                            break
                        except:
                            continue
                    continue
                shutil.move(f'{output_folder_path}/{el}',f'{output_folder_path}/{id}/{el}')
            except:
                try:
                    shutil.move(f'{output_folder_path}/{el}',f'{output_folder_path}/unresolved/{str(datetime.datetime.now()).replace(":", "-").replace(".", "-")}{el}')
                except:
                    shutil.move(f'{output_folder_path}/{el}',f'{output_folder_path}/unresolved/{str(datetime.datetime.now()).replace(":","-").replace(".","-")}{el}')

                pass
    pass
# extract_images()
def check_if_any_new():
    for f in os.listdir(output_folder_path):
        if os.path.isfile(os.path.join(output_folder_path,f)):
            return True

def run_process():
    extract_images_()
    if check_if_any_new():
        print('new')
        set_env_var()
        organize_images()
def main():
    while True:
        print('Running ==')
        run_process()
        print('Completed ==')
        time.sleep(30)
