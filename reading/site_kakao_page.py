from email import header
import os, sys, traceback, json, urllib.parse, requests, argparse, yaml, platform, time, threading, re, base64, fnmatch
import traceback, unicodedata
from datetime import datetime
import urllib.request as py_urllib2
import urllib.parse as py_urllib #urlencode

from lxml import html, etree
import xmltodict

if platform.system() == 'Windows':
    sys.path += ["C:\SJVA3\lib2", "C:\SJVA3\data\custom", "C:\SJVA3_DEV"]
else:
    sys.path += ["/root/SJVA3/lib2", "/root/SJVA3/data/custom", '/root/SJVA3_DEV']

from support.base import get_logger, d, default_headers, SupportFile, SupportString
logger = get_logger()
from urllib.parse import quote
import lxml.html
from lxml import etree
import re
from collections import OrderedDict 



class SiteKakaoPage():
    @classmethod
    def search(cls, title, auth=''):
        try:
            url = f"https://page.kakao.com/search?word={quote(title)}"
            text = requests.get(url, headers=default_headers).text
            root = lxml.html.fromstring(text)
            tags = root.xpath('//*[@id="root"]/div[3]/div/div/div[2]/div')
            #logger.error(tags)
            ret = []
            for tag in tags:
                entity = {}
                entity['code'] = tag.xpath('.//a')[0].attrib['href']
                entity['title'] = tag.xpath('.//div/a/div[2]/div[1]/span')[0].text_content()
                tmps = tag.xpath('.//div/a/div[2]/div[2]/div[1]/div')
                text = []
                for tmp in tmps:
                    text.append(tmp.text_content())
                entity['author'] = ' '.join(text)
                ret.append(entity)
            return ret
        except:
            pass

    @classmethod
    def info(cls, code):
        try:
            #url = f"https://page.kakao.com{code}"
            #text = requests.get(url, headers=default_headers).text
            #root = lxml.html.fromstring(text)
            seriesid = code.split('seriesId=')[1]
            url = f"https://api2-page.kakao.com/api/v4/store/seriesdetail?seriesid={seriesid}"
            data = {'seriesid': seriesid}
            data = requests.post(url, headers=default_headers, data=data).json()
            #logger.debug(d(data))
            ret = {}
            for tmp in data['authors_other']:
                if str(tmp['id']) == seriesid:
                    ret['poster'] = f"https://dn-img-page.kakao.com/download/resource?kid={tmp['image_url']}"
                    ret['premiered'] = tmp['create_dt'].split(' ')[0].replace('-', '')

            ret['title'] = data['seriesdetail']['title']
            ret['desc'] = data['seriesdetail']['description']
            #ret['poster'] = 'https:' + root.xpath('//*[@id="root"]/div[3]/div/div/div[1]/div[1]/div[1]/img')[0].attrib['src'].split('&')[0]
            ret['author'] = data['seriesdetail']['author_name']
            ret['publisher'] = data['seriesdetail']['publisher_name']
            ret['tag'] = ['카카오페이지']
            ret['genre'] = data['seriesdetail']['sub_category']
            return ret
        except Exception as exception:
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
       


if __name__ == '__main__':
    data = SiteKakaoPage.search('악녀를 죽여 줘')
    logger.debug(d(data))
    data = SiteKakaoPage.info(data[0]['code'])
    logger.debug(d(data))



