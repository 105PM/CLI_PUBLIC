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
            ret = {}

            url = f"https://page.kakao.com/_next/data/2.5.3/content/{seriesid}.json"
            data = requests.get(url, headers=default_headers).json()
            ret['title'] = data['pageProps']['metaInfo']['ogTitle']
            ret['poster'] = f"https:{data['pageProps']['metaInfo']['image'].split('&')[0]}"
            ret['desc'] = data['pageProps']['metaInfo']['description']
            ret['author'] = data['pageProps']['metaInfo']['author']
            ret['publisher'] = data['pageProps']['initialState']['json']['contentHome']['fetching']['about'][seriesid]['data']['detail']['publisherName']

            url = f"https://page.kakao.com/graphql"
            query = {
                "query": "query contentHomeOverview($seriesId: Long!) {\n  contentHomeOverview(seriesId: $seriesId) {\n    id\n    seriesId\n    displayAd {\n      ...DisplayAd\n      ...DisplayAd\n      __typename\n    }\n    content {\n      ...SeriesFragment\n      __typename\n    }\n    displayAd {\n      ...DisplayAd\n      __typename\n    }\n    relatedKeytalk {\n      id\n      categoryUid\n      groupUid\n      groupType\n      name\n      order\n      __typename\n    }\n    lastNoticeDate\n    __typename\n  }\n}\n\nfragment DisplayAd on DisplayAd {\n  sectionUid\n  bannerUid\n  treviUid\n  momentUid\n}\n\nfragment SeriesFragment on Series {\n  id\n  seriesId\n  title\n  thumbnail\n  categoryUid\n  category\n  subcategoryUid\n  subcategory\n  badge\n  isAllFree\n  isWaitfree\n  isWaitfreePlus\n  is3HoursWaitfree\n  ageGrade\n  state\n  onIssue\n  seriesType\n  businessModel\n  authors\n  pubPeriod\n  freeSlideCount\n  lastSlideAddedDate\n  waitfreeBlockCount\n  waitfreePeriodByMinute\n  bm\n  saleState\n  serviceProperty {\n    ...ServicePropertyFragment\n    __typename\n  }\n  operatorProperty {\n    ...OperatorPropertyFragment\n    __typename\n  }\n  assetProperty {\n    ...AssetPropertyFragment\n    __typename\n  }\n}\n\nfragment ServicePropertyFragment on ServiceProperty {\n  viewCount\n  readCount\n  ratingCount\n  ratingSum\n  commentCount\n  pageContinue {\n    ...ContinueInfoFragment\n    __typename\n  }\n  todayGift {\n    ...TodayGift\n    __typename\n  }\n  waitfreeTicket {\n    ...WaitfreeTicketFragment\n    __typename\n  }\n  isAlarmOn\n  isLikeOn\n  ticketCount\n  purchasedDate\n  lastViewInfo {\n    ...LastViewInfoFragment\n    __typename\n  }\n  purchaseInfo {\n    ...PurchaseInfoFragment\n    __typename\n  }\n}\n\nfragment ContinueInfoFragment on ContinueInfo {\n  title\n  isFree\n  productId\n  lastReadProductId\n  scheme\n  continueProductType\n  hasNewSingle\n  hasUnreadSingle\n}\n\nfragment TodayGift on TodayGift {\n  id\n  uid\n  ticketType\n  ticketKind\n  ticketCount\n  ticketExpireAt\n  isReceived\n}\n\nfragment WaitfreeTicketFragment on WaitfreeTicket {\n  chargedPeriod\n  chargedCount\n  chargedAt\n}\n\nfragment LastViewInfoFragment on LastViewInfo {\n  isDone\n  lastViewDate\n  rate\n  spineIndex\n}\n\nfragment PurchaseInfoFragment on PurchaseInfo {\n  purchaseType\n  rentExpireDate\n}\n\nfragment OperatorPropertyFragment on OperatorProperty {\n  thumbnail\n  copy\n  torosImpId\n  torosFileHashKey\n  isTextViewer\n}\n\nfragment AssetPropertyFragment on AssetProperty {\n  bannerImage\n  cardImage\n  cardTextImage\n  cleanImage\n  ipxVideo\n}\n",
                "operationName": "contentHomeOverview",
                "variables": {
                    "seriesId": seriesid
                }
            }
            kakao_headers = default_headers
            kakao_headers['content-type'] = 'application/json'
            data = requests.post(url, data=json.dumps(query), headers=kakao_headers).json()
            # logger.debug(d(data))

            ret['premiered'] = data['data']['contentHomeOverview']['content']['lastSlideAddedDate'].split('T')[0].replace('-','')
            ret['tag'] = ['카카오페이지']
            ret['genre'] = data['data']['contentHomeOverview']['content']['subcategory']
            return ret
        except Exception as exception:
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    data = SiteKakaoPage.search('0레벨 플레이어')
    logger.debug(d(data))
    data = SiteKakaoPage.info(data[0]['code'])
    logger.debug(d(data))
