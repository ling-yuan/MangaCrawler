from typing import Iterable
import scrapy
from scrapy import Request
from scrapy import Selector
from scrapy.http import Response

from MangaCrawler.items import MhItem, ChapterItem


class BaozimhSpider(scrapy.Spider):
    name = "baozimh"
    allowed_domains = ["baozimh.one"]

    # start_urls = ["https://baozimh.one/"]

    def start_requests(self) -> Iterable[Request]:
        '''起始请求'''
        for i in range(1, 2):  # 991
            url = f'https://baozimh.one/manga/page/{i}'
            yield Request(url=url, callback=self.parse_mhlist)

    def parse_mhlist(self, response: Response, **kwargs):
        '''解析漫画列表'''
        sel = Selector(response)
        mh_list = sel.css('div[class*="cardlist"] > div > a')

        for mh in mh_list:
            mh_url = mh.css('::attr(href)').extract_first()
            mh_url = response.urljoin(mh_url)
            mh_url = mh_url.replace('/manga', '/chapterlist')
            mh_title = mh.css('h3.cardtitle::text').extract_first().strip()

            mh_item = MhItem()
            mh_item['mh_title'] = mh_title
            mh_item['mh_url'] = mh_url
            mh_item['mh_chapter_list'] = []
            mh_item['mh_chapter_length'] = 0

            yield Request(url=mh_url, callback=self.parse, cb_kwargs={'mh_item': mh_item})

    def parse(self, response: Response, **kwargs):
        '''解析漫画章节列表'''

        mh_item = kwargs['mh_item']

        sel = Selector(response)

        chapter_list = sel.css('#chapterlists > div > a')
        mh_item['mh_chapter_length'] = len(chapter_list)

        for chapter in chapter_list:
            chapter_url = chapter.css('::attr(href)').extract_first() or ''
            if chapter_url == '':
                continue

            chapter_url = response.urljoin(chapter_url)
            chapter_title = chapter.css('div > span:nth-child(1)::text').extract_first()
            chapter_time = chapter.css('div > span:nth-child(2)::text').extract_first()

            yield Request(url=chapter_url, callback=self.parse_chapter, cb_kwargs={'chapter_title': chapter_title.strip(), 'chapter_time': chapter_time.strip(), 'chapter_url': chapter_url.strip(), 'mh_item': mh_item})

    def parse_chapter(self, response: Response, **kwargs):
        '''解析漫画章节内容'''

        chapter_item = ChapterItem()
        chapter_item['chapter_title'] = kwargs['chapter_title']
        chapter_item['chapter_time'] = kwargs['chapter_time']
        chapter_item['chapter_url'] = kwargs['chapter_url']

        sel = Selector(response)
        img_list = sel.css('div.w-full.h-full > img::attr(data-src)').extract()
        chapter_item['chapter_content_url_list'] = img_list

        mh_item = kwargs['mh_item']
        mh_item['mh_chapter_list'].append(chapter_item)

        if mh_item['mh_chapter_length'] == len(mh_item['mh_chapter_list']):
            yield mh_item
        else:
            yield None
