import os, sys, traceback, json, urllib.parse, requests, argparse, yaml, platform, time, threading, re, base64, fnmatch
from datetime import datetime, timedelta
from urllib.parse import quote
from difflib import SequenceMatcher 
import shutil, copy
import zipfile

if platform.system() == 'Windows':
    sys.path += ["C:\SJVA3\lib2", "C:\SJVA3\data\custom", "C:\SJVA3_DEV"]
else:
    sys.path += ["/root/SJVA3/lib2", "/root/SJVA3/data/custom", '/root/SJVA3_DEV']
from support.base import get_logger, d, default_headers, SupportFile, SupportString
logger = get_logger()

from site_naver_book import SiteNaverBook
from site_naver_series import SiteNaverSeries
from site_kakao_page import SiteKakaoPage



class MakeInfo:

    def __init__(self, main, config):
        self.main = config
        self.config = config



    def start(self):
        source = self.config['source']
        target = self.config['target']
        for folder in sorted(os.listdir(source)):
            try:
                pass_flag = False
                filepath = os.path.join(source, folder)
                is_folder = True
                if os.path.isdir(filepath):
                    logger.info(f"현재폴더 : {folder}")
                    child = sorted(os.listdir(os.path.join(source, folder)))
                    logger.debug(d(child))
                    """
                    for c in child:
                        if c.lower().endswith('.txt'):
                            logger.error("텍스트 포함")
                            #shutil.move(filepath, self.config["텍스트 이동"])
                            pass_flag = True
                            break
                    else:
                        logger.debug(d(child))
                    """
                    if pass_flag:
                        continue
                elif os.path.splitext(filepath)[-1].lower() == '.epub':
                    logger.info(f"현재파일 : {folder}")
                    is_folder = False
                else:
                    continue
                #if self.append_page_count(filepath) == False:
                #    logger.error("변환 에러")
                #    continue

                search_name = folder
                if is_folder == False:
                    search_name = os.path.splitext(folder)[0]

                data = self.input_title(search_name)
                if data == None:
                    continue

                while True:
                    
                    for idx, item in enumerate(data):
                        #logger.debug(d(item))
                        logger.warning(f"[{idx}] {item['title']} / {item['author']}")

                    index = input("책 선택 (00:책 입력 ): ")
                    if index == '':
                        pass_flag = True
                        break
                    elif index == '00':
                        search_name = folder
                        if is_folder == False:
                            search_name = os.path.splitext(folder)[0]
                        data = self.input_title(search_name, is_first=False)
                        if data == None:
                            pass_flag = True
                            break
                        continue
                    try:
                        index = int(index)
                    except:
                        logger.error("다시 입력")
                        continue
                    
                    
                    try:
                        select_item = data[index]
                        info = self.info(data[index]['code'], select_item)
                    except:
                        info = None
                    
                    if info == None:
                        logger.error("info 에러")
                        continue
                    logger.debug(d(info))    
                        

                    ans = input("처리 여부 (00:책선택) : ")
                    if ans == '00':
                        continue
                    if ans.lower() not in ['y', 'ㅛ', '0']:
                        pass_flag = True
                        break
                    break
                
                if pass_flag:
                    continue
                
                # 폴더명 변경
                #title = info['title'].replace('. 1', '').strip()
                title = re.sub('\.\s\d+$', '', info['title']).strip()
                if target != None and target != '':
                    target_foldername = f"{title} [{info['author'].split(',')[0].strip()}]"
                    target_foldername = SupportFile.text_for_filename(target_foldername)
                    targetpath = os.path.join(target, target_foldername)
                    if self.config['use_cate']:
                        targetpath = os.path.join(target, SupportString.get_cate_char_by_first(target_foldername),  target_foldername)
                    else:
                        targetpath = os.path.join(target, target_foldername)

                    if is_folder:
                        if os.path.exists(targetpath):
                            logger.error("이미 폴더 있음")
                            continue
                        shutil.move(filepath, targetpath)
                    else:
                        os.makedirs(targetpath)
                        shutil.move(filepath, targetpath)
                else:
                    targetpath = filepath

                # 폴더안에 []로 작가 이름이 있으면 지움
                """
                for filename in os.listdir(targetpath):
                    #tmp = filename.replace(f"[{info['author']}]", '').strip()
                    tmp = re.sub("\[.*?\]", '', filename).strip()
                    #tmp = tmp.replace(' (소설)', '').strip()
                    tmp = re.sub("\s+\(.*?\)", '', tmp).strip()
                    if filename != tmp:
                        os.rename(os.path.join(targetpath, filename), os.path.join(targetpath, tmp))
                """
                coverfilepath = os.path.join(targetpath, '[Cover].jpg')
                if os.path.exists(coverfilepath):
                    os.remove(coverfilepath)


                # cover.jpg
                if self.config['cover']:
                    coverfilepath = os.path.join(targetpath, 'cover.jpg')
                    if os.path.exists(coverfilepath) == False:
                        ret = SupportFile.download(info['poster'], coverfilepath)
                        if ret == False:
                            logger.error("이미지 파일 없음")
                
                tmp = XML.format(
                    title = change(title),
                    desc = change(info['desc']),
                    author = change(info['author']),
                    publisher = change(info['publisher']),
                    year = info['premiered'][0:4],
                    month = info['premiered'][4:6] if len(info['premiered']) > 4 else '01',
                    day = info['premiered'][6:8] if len(info['premiered']) > 6 else '01',
                    tags = ', '.join(info['tag']) if 'tag' in info  else '',
                    inker = '',
                    genre = ', '.join(info['genre']) if 'genre' in info  else '',
                )
                SupportFile.write_file(os.path.join(targetpath, 'info.xml'), tmp)
                continue
            except Exception as exception:
                logger.error('Exception:%s', exception)
                logger.error(traceback.format_exc())


    def input_title(self, folder, is_first=True):
        while True:
            if is_first:
                search_name = '0'
                is_first = False
            else:
                search_name = input("책 제목 입력 (m:NO META 이동): ")
            if search_name == '':
                return
            if search_name in ['.', '0']:
                search_name = folder
                search_name = search_name.replace('@ 完', '').replace('㉿ 完', '').strip()
                #search_name = search_name.replace('(소설)', '').strip()
                search_name = re.sub("\(.*?\)", '', search_name).strip()
                
                match = re.search('\[(?P<author>.*?)\]', search_name)
                if match:
                    search_name = re.sub("\[.*?\]", '', search_name).strip()
                    search_name += f"|{match.group('author')}"
            if search_name.lower() in ['m', 'ㅡ']:
                target = os.path.join(self.config['no_meta_target'])
                logger.warning("노 메타 폴더 이동 : ")
                shutil.move(os.path.join(self.config['source'], folder), target)
                return

            data = self.search(search_name)
            if data == None or len(data) == 0:
                logger.error("책 없음")
                continue
            return data


    def search(self, param):
        tmp = param.split('|')
        if len(tmp) == 1:
            title = tmp[0]
            author = ''
        else:
            title = tmp[0]
            author = tmp[1]

        if self.config['meta_source'] == 'naverbook':
            data = SiteNaverBook.search(title, author, '', '', '')
            if data['ret'] != 'success':
                return
            return data['data']

        elif self.config['meta_source'] == 'naverseries':
            data = SiteNaverSeries.search(title, author)
            return data
        elif self.config['meta_source'] == 'kakaopage':
            data = SiteKakaoPage.search(title, author)
            return data


    def info(self, code, select_item=None):
        if self.config['meta_source'] == 'naverbook':
            try:
                info = SiteNaverBook.info(code)
            except:
                info = None
            
            if info == None:
                logger.error("책 정보 가져올수 없음")
                logger.debug(d(select_item))
                try:
                    info = {}
                    info['title'] = re.sub('\s\d+$', '', select_item['title']).strip()
                    info['poster'] = select_item['image'].split('?')[0]
                    info['desc'] = select_item['description']
                    info['publisher'] = select_item['publisher']
                    #info['premiered'] = select_item['image'].split('date=')[1]
                    info['premiered'] = select_item['pubdate']
                    info['author'] = select_item['author']
                    logger.debug(info)
                except Exception as exception:
                    logger.error('Exception:%s', exception)
                    logger.error(traceback.format_exc())
            return info

        elif self.config['meta_source'] == 'naverseries':
            data = SiteNaverSeries.info(code)
            return data
        elif self.config['meta_source'] == 'kakaopage':
            data = SiteKakaoPage.info(code)
            return data
                    





XML = '''<?xml version="1.0"?>
<ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Title>{title}</Title>
  <Series>{title}</Series>
  <Summary>{desc}</Summary>
  <Writer>{author}</Writer>
  <Publisher>{publisher}</Publisher>
  <Genre></Genre>
  <Tags>{tags}</Tags>
  <LanguageISO>ko</LanguageISO>
  <Notes>완결</Notes>
  <CoverArtist></CoverArtist>
  <Penciller></Penciller>
  <Inker>{inker}</Inker>
  <Colorist></Colorist>
  <Letterer></Letterer>
  <CoverArtist></CoverArtist>
  <Editor></Editor>
  <Characters></Characters>
  <Year>{year}</Year>
  <Month>{month}</Month>
  <Day>{day}</Day>
</ComicInfo>'''


def change(str):
    return str.replace('<', '"').replace('>', '"').replace('&', '&amp;').strip()
                    
                
