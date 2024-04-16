import time
import scrapy
from scrapy.http import JsonRequest, Response

from MangaCrawler.items import ChapterItem, MhItem


# 时间戳转换
def ts_to_time(ts):
    return time.strftime('%Y/%m/%d', time.localtime(int(ts)))


class DmzjSpider(scrapy.Spider):
    name = "dmzj"
    allowed_domains = ["www.idmzj.com"]

    # start_urls = ["https://www.idmzj.com"]

    def start_requests(self):
        '''起始请求'''
        url = 'https://www.idmzj.com/api/v1/comic1/filter?'
        for i in range(1, 2):  # 1212页
            params = {'channel': 'pc', 'app_name': 'dmzj', 'version': '1.0.0', 'page': i, 'size': 18}
            for key, value in params.items():
                url = url + f'{key}={value}&'
            url = url[:-1]
            yield scrapy.Request(url=url, callback=self.parse)
            # yield JsonRequest(url=url, method="GET", data=params, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        '''解析漫画列表'''
        data = response.json()

        # comic_list = data.get('data').get('comicList')
        comic_list = data['data']['comicList']
        print(comic_list)
        for comic in comic_list:
            mh_item = MhItem()
            mh_item['mh_refer'] = 'dmzj'
            mh_item['mh_title'] = comic['name']
            mh_item['mh_url'] = response.urljoin(f'/info/{comic["comic_py"]}.html')
            mh_item['mh_chapter_list'] = []
            mh_item['mh_chapter_length'] = 0

            url = 'https://www.idmzj.com/api/v1/comic1/comic/detail?'
            params = {
                'channel': 'pc',
                'app_name': 'dmzj',
                'version': '1.0.0',
                'comic_py': comic["comic_py"],
            }
            for key, value in params.items():
                url = url + f'{key}={value}&'
            url = url[:-1]

            # 负载不同，但url相同，需要设置dont_filter=True，否则会被调度器认为是重复请求
            yield scrapy.Request(url=url, callback=self.parse_chapter_list, cb_kwargs={'mh_item': mh_item, 'comic_py': comic["comic_py"]}, dont_filter=True)

    def parse_chapter_list(self, response: Response, **kwargs):
        '''解析漫画章节列表'''
        mh_item = kwargs['mh_item']
        data = response.json()

        errno = data['errno']
        if errno != 0:
            yield mh_item
        else:
            mh_id = data['data']['comicInfo']['id']
            chapter_list = data['data']['comicInfo']['chapterList']
            if chapter_list == None:
                yield mh_item
            else:
                chapter_list = chapter_list[0]['data']
                mh_item['mh_chapter_length'] = len(chapter_list)
                print(chapter_list)
                i = 0
                for chapter in chapter_list:
                    url = 'https://www.idmzj.com/api/v1/comic1/chapter/detail?'
                    params = {
                        'channel': 'pc',
                        'app_name': 'dmzj',
                        'version': '1.0.0',
                        'comic_id': mh_id,
                        'chapter_id': chapter['chapter_id'],
                    }

                    for key, value in params.items():
                        url = url + f'{key}={value}&'
                    url = url[:-1]

                    chapter_url = response.urljoin(f"/view/{kwargs['comic_py']}/{chapter['chapter_id']}.html")
                    chapter_time_ts = chapter['updatetime']

                    yield scrapy.Request(url=url, callback=self.parse_chapter_content, cb_kwargs={'mh_item': mh_item, 'chapter_url': chapter_url, 'chapter_num': i, 'chapter_time': chapter_time_ts}, dont_filter=True)

    def parse_chapter_content(self, response: Response, **kwargs):
        '''解析漫画章节内容'''
        mh_item = kwargs['mh_item']
        data = response.json()

        chapter_item = ChapterItem()
        chapter_item['chapter_num'] = kwargs['chapter_num']
        chapter_item['chapter_title'] = data['data']['chapterInfo']['title']
        chapter_item['chapter_time'] = ts_to_time(kwargs['chapter_time'])
        chapter_item['chapter_url'] = kwargs['chapter_url']
        chapter_item['chapter_content_url_list'] = data['data']['chapterInfo']['page_url']

        mh_item['mh_chapter_list'].append(chapter_item)

        if mh_item['mh_chapter_length'] == len(mh_item['mh_chapter_list']):
            yield mh_item
        # else:
        #     yield None
