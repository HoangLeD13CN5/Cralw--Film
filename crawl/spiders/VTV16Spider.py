# -*- coding: utf-8 -*-
import scrapy
from crawl.items import CrawlItem, TypeMovie
from scrapy_splash import SplashRequest


class VTV16Spider(scrapy.Spider):
    name = "vtv16"
    allowed_domains = ['vtv16.com']
    start_urls = ['http://www.vtv16.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, endpoint="render.html", callback=self.parse)

    def parse(self, response):
        url = response.xpath('//div[@id="menu"]//li/a[contains(.,"Phim lẻ")]/@href').get()
        item = CrawlItem()
        item['type'] = TypeMovie.oddMovies
        request = SplashRequest(url, endpoint="render.html", callback=self.parse_list)
        request.meta['film'] = item
        yield request

    def parse_list(self, response):
        film = response.meta['film'].copy()
        for element in response.xpath('//ul[@class="list-film"]/li/div/h4'):
            url = element.xpath('.//a/@href').extract_first('').strip()
            request = SplashRequest(url, endpoint="render.html", callback=self.parse_detail)
            request.meta['film'] = film
            yield request
        next_page_url = response.xpath('//div[@class="page-navigation"]//'
                                       'a[preceding-sibling::a[contains(@class,"current")]][1]/@href').get()
        if next_page_url:
            request_next_page = SplashRequest(next_page_url,
                                              endpoint="render.html", callback=self.parse_list)
            request_next_page.meta['film'] = film
            yield request_next_page

    def parse_detail(self, response):
        film = response.meta['film'].copy()
        film['url_root'] = self.start_urls[0]
        film["url"] = response.urljoin(response.xpath('//a[@id="btn-film-watch"]/@href')
                                       .extract_first(response.url).strip())
        film["title"] = response.xpath('//div[@class="details"]/h1/a/text()').get().strip()
        film["title_english"] = response.xpath('//div[@class="details"]/h2/text()').get().strip()
        film["thumbnail"] = response.xpath('//div[@class="thumb"]/img/@src').get().strip()

        kind = ""
        for element in response.xpath('//dd[preceding-sibling::dt[contains(.,"Thể loại:")]][1]/a/text()'):
            kind += str(element.get()) + ","
        film["kind"] = kind[:-1]

        film["duration"] = response.xpath('//dd[preceding-sibling::'
                                          'dt[contains(.,"Thời lượng")]][1]/text()').get().strip()
        film["status"] = response.xpath('//dd[preceding-sibling::'
                                        'dt[contains(.,"Đang chiếu:")]][1]//text()').get().strip()

        actors = ""
        for element in response.xpath('//dd[preceding-sibling::dt[contains(.,"Diễn viên:")]][1]/a/text()'):
            actors += str(element.get()) + ","
        film["actors"] = actors[:-1]

        director = ""
        for element in response.xpath('//dd[preceding-sibling::dt[contains(.,"Đạo diễn:")]][1]/a/text()'):
            director += str(element.get()) + ","
        film["director"] = director[:-1]

        film["release_year"] = response.xpath('//dd[preceding-sibling::'
                                              'dt[contains(.,"Năm phát hành")]][1]/text()').get().strip()
        film["views"] = response.xpath('//dd[preceding-sibling::dt[contains(.,"Lượt xem:")]][1]/text()').get().strip()
        film["imdb"] = "5.0"

        for element in response.xpath('//div[@id="pagetext"]/text()'):
            if len(element.get()) > 20:
                film["description"] = element.get().strip()

        yield film
