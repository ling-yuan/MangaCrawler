import scrapy
from scrapy.http import JsonRequest, Response

from MangaCrawler.items import MhItem


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
            yield scrapy.Request(url=url, callback=self.parse_chapter_list, cb_kwargs={'mh_item': mh_item}, dont_filter=True)

    def parse_chapter_list(self, response: Response, **kwargs):
        '''解析漫画章节列表'''
        mh_item = kwargs['mh_item']
        data = response.json()

        errno = data['errno']
        if errno != 0:
            yield mh_item
        else:
            chapter_list = data['data']['comicInfo']['chapterList']
            if chapter_list == None:
                yield mh_item
            else:
                chapter_list = chapter_list[0]['data']
                print(chapter_list)
                yield mh_item
