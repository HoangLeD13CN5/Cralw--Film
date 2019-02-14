# -*- coding: utf-8 -*-
import scrapy
from crawl.items import CrawlItem, TypeMovie
from scrapy_splash import SplashRequest


class KhoaiTVSpider(scrapy.Spider):
    name = "khoaitv"
    name_web = "khoai.tv"
    allowed_domains = ['khoai.tv']
    start_urls = ['https://khoai.tv/']
    is_cralw_all = False

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, endpoint="render.html", callback=self.parse)

    def parse(self, response):
        url = response.xpath('//li[@class="dropdown"]/a[contains(.,"Phim Lẻ")]/@href').get()
        item = CrawlItem()
        item['type'] = TypeMovie.oddMovies.value
        request = SplashRequest(url, endpoint="render.html", callback=self.parse_list)
        request.meta['film'] = item
        yield request

        url_suite = response.xpath('//li[@class="dropdown"]/a[contains(.,"Phim Bộ")]/@href').get()
        item_suite = CrawlItem()
        item_suite['type'] = TypeMovie.suiteMovies.value
        request_suite = SplashRequest(url_suite, endpoint="render.html", callback=self.parse_list)
        request_suite.meta['film'] = item_suite
        yield request_suite

    def parse_list(self, response):
        film = response.meta['film'].copy()
        for element in response.xpath('//div[@class="group-film group-film-category"]/div'):
            url = element.xpath('.//a/@href').extract_first('').strip()
            thumbnail = response.xpath('//div[@class="poster-film-small"]/@style').get()
            thumbnail_list = thumbnail.split('(')
            film["thumbnail"] = thumbnail_list[1][:-1]
            request = SplashRequest(url, endpoint="render.html", callback=self.parse_detail)
            request.meta['film'] = film
            yield request
        if self.is_cralw_all:
            next_page_url = response.xpath('//li[@class="pag-next"]/a/@href').get()
            if next_page_url:
                request_next_page = SplashRequest(next_page_url,
                                                  endpoint="render.html", callback=self.parse_list)
                request_next_page.meta['film'] = film
                yield request_next_page

    def parse_detail(self, response):
        film = response.meta['film'].copy()
        film['nameWeb'] = self.name_web
        film['url_root'] = self.start_urls[0]
        film["url"] = response.xpath('//a[@class="play-film"]/@href').get().strip()
        film["title"] = response.xpath('//h1[@class="title-film-detail-1"]/text()').get().strip()
        film["title_english"] = response.xpath('//h2[@class="title-film-detail-2"]/text()').get().strip()

        kind = ""
        for element in response.xpath('//ul[@class="infomation-film"]/li[contains(.,"Thể loại")]/a/text()'):
            kind += str(element.get()) + ","
        film["kind"] = kind[:-1]

        film["duration"] = response.xpath('//ul[@class="infomation-film"]/'
                                          'li[contains(.,"Thời lượng")]/span/text()').get().strip()
        status = response.xpath('//ul[@class="infomation-film"]/li[contains(.,"Số tập")]/span/text()').get().strip()
        if status:
            film["status"] = status
        else:
            film["status"] = ""

        actors = ""
        for element in response.xpath('//ul[@class="infomation-film"]/li[contains(.,"Diễn viên")]/a/text()'):
            actors += str(element.get()) + ","
        film["actors"] = actors[:-1]

        film["director"] = response.xpath('//ul[@class="infomation-film"]/'
                                          'li[contains(.,"Đạo diễn")]/span/text()').get().strip()

        film["release_year"] = response.xpath('//ul[@class="infomation-film"]/'
                                              'li[contains(.,"Ngày phát hành")]/span/text()').get().strip()
        film["views"] = "400 "
        film["imdb"] = response.xpath('//div[@class="imdb"]/text()').get().strip()
        film["description"] = response.xpath('//p[@class="content-film"]/text()').get().strip()
        yield film
