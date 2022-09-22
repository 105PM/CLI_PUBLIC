from email import header
import os, sys, traceback, json, urllib.parse, requests, argparse, yaml, platform, time, threading, re, base64, fnmatch
import traceback, unicodedata
from datetime import datetime
import urllib.request as py_urllib2
import urllib.parse as py_urllib  # urlencode

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
            url = f"https://page.kakao.com/graphql"
            data = {
                "query": "query SearchKeyword($input: SearchKeywordInput!) {\n  searchKeyword(searchKeywordInput: $input) {\n    id\n    list {\n      ...NormalListViewItem\n      __typename\n    }\n    total\n    isEnd\n    keyword\n    sortOptionList {\n      ...SortOption\n      __typename\n    }\n    selectedSortOption {\n      ...SortOption\n      __typename\n    }\n    categoryOptionList {\n      ...SortOption\n      __typename\n    }\n    selectedCategoryOption {\n      ...SortOption\n      __typename\n    }\n    showOnlyComplete\n    __typename\n  }\n}\n\nfragment NormalListViewItem on NormalListViewItem {\n  id\n  type\n  ticketUid\n  thumbnail\n  badgeList\n  ageGradeBadge\n  ageGrade\n  isAlaramOn\n  row1\n  row2\n  row3 {\n    id\n    metaList\n    __typename\n  }\n  row4\n  row5\n  scheme\n  continueScheme\n  nextProductScheme\n  continueData {\n    ...ContinueInfoFragment\n    __typename\n  }\n  torosImpId\n  torosFileHashKey\n  seriesId\n  isCheckMode\n  isChecked\n  isReceived\n  showPlayerIcon\n  rank\n  isSingle\n  singleSlideType\n  ageGrade\n  eventLog {\n    ...EventLogFragment\n    __typename\n  }\n  giftEventLog {\n    ...EventLogFragment\n    __typename\n  }\n}\n\nfragment ContinueInfoFragment on ContinueInfo {\n  title\n  isFree\n  productId\n  lastReadProductId\n  scheme\n  continueProductType\n}\n\nfragment EventLogFragment on EventLog {\n  click {\n    layer1\n    layer2\n    setnum\n    ordnum\n    copy\n    imp_id\n    imp_provider\n    __typename\n  }\n  eventMeta {\n    id\n    name\n    subcategory\n    category\n    series\n    provider\n    series_id\n    type\n    __typename\n  }\n  viewimp_contents {\n    type\n    name\n    id\n    imp_area_ordnum\n    imp_id\n    imp_provider\n    imp_type\n    layer1\n    layer2\n    __typename\n  }\n  customProps {\n    landing_path\n    view_type\n    toros_imp_id\n    toros_file_hash_key\n    toros_event_meta_id\n    content_cnt\n    event_series_id\n    event_ticket_type\n    play_url\n    __typename\n  }\n}\n\nfragment SortOption on SortOption {\n  id\n  name\n  param\n}\n",
                "operationName": "SearchKeyword",
                "variables": {
                    "input": {
                        "page": 0,
                        "size": 25,
                        "keyword": title
                    }
                }
            }
            kakao_headers = default_headers
            kakao_headers['content-type'] = 'application/json'
            res = requests.post(url, data=json.dumps(data), headers=kakao_headers).json()['data']['searchKeyword']['list']
            ret = []
            for book in res:
                entity = {}
                entity['code'] = book['eventLog']['eventMeta']['id']
                entity['title'] = book['row1']
                entity['author'] = book['row2'][2]
                ret.append(entity)
            return ret
        except:
            pass

    @classmethod
    def info(cls, code):
        try:
            # url = f"https://page.kakao.com{code}"
            # text = requests.get(url, headers=default_headers).text
            # root = lxml.html.fromstring(text)
            seriesid = code
            url = f"https://api2-page.kakao.com/api/v4/store/seriesdetail?seriesid={seriesid}"
            data = {'seriesid': seriesid}
            data = requests.post(url, headers=default_headers, data=data).json()
            # logger.debug(d(data))
            ret = {}
            for tmp in data['authors_other']:
                if str(tmp['id']) == seriesid:
                    ret['poster'] = f"https://dn-img-page.kakao.com/download/resource?kid={tmp['image_url']}"
                    ret['premiered'] = tmp['create_dt'].split(' ')[0].replace('-', '')

            ret['title'] = data['seriesdetail']['title']
            ret['desc'] = data['seriesdetail']['description']
            # ret['poster'] = 'https:' + root.xpath('//*[@id="root"]/div[3]/div/div/div[1]/div[1]/div[1]/img')[0].attrib['src'].split('&')[0]
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
