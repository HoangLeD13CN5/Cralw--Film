import scrapy
from crawl.items import CrawlItem, TypeMovie
from scrapy_splash import SplashRequest


class BomTanSpider(scrapy.Spider):
    name = "phimmoi"
    allowed_domains = ['phimmoi.net']
    start_urls = ['http://www.phimmoi.net/']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, endpoint="render.html", callback=self.parse)

    def parse(self, response):
        # film one series
        one_series_movie_url = response.xpath('//div[@class="container"]/ul/'
                                              'li/a[contains(.,"Phim lẻ")]/@href').extract_first('').strip()
        item = CrawlItem()
        item['type'] = TypeMovie.oddMovies
        request = SplashRequest(response.urljoin(one_series_movie_url),
                                endpoint="render.html", callback=self.parse_list)
        request.meta['film'] = item
        yield request

    def parse_list(self, response):
        film = response.meta['film'].copy()
        for element in response.xpath('//ul[@class="list-movie"]/li'):
            url = element.xpath('.//a/@href').extract_first('').strip()
            request = SplashRequest(response.urljoin(url), endpoint="render.html", callback=self.parse_detail)
            request.meta['film'] = film
            yield request
        next_page_url = response.xpath('//ul/li/a[contains(.,"Trang kế")]/@href').get()
        print("Next Page: " + str(next_page_url))
        request_next_page = SplashRequest(response.urljoin(str(next_page_url)),
                                          endpoint="render.html", callback=self.parse_list)
        request_next_page.meta['film'] = film
        yield request_next_page

    def parse_detail(self, response):
        film = response.meta['film'].copy()
        film['url_root'] = self.start_urls[0]
        film["url"] = response.xpath('//div[@class="movie-l-img"]/ul/li/a[contains(.,"Xem phim")]/@href').get()

        film["title"] = response.xpath('//div[@class="movie-info"]//h1/span/a/text()').get()

        film["title_english"] = response.xpath('//div[@class="movie-info"]//h1/span[@class="title-2"]/text()').get()
        film["thumbnail"] = response.xpath('//div[@class="movie-info"]//div[@class="movie-l-img"]/img/@src').get()
        film["kind"] = response.xpath('//div[@class="movie-info"]//div//a[@class="category"]/text()').get()
        film["duration"] = response.xpath('//dd[preceding-sibling::dt[contains(.,"Thời lượng")]][1]/text()').get()
        film["status"] = response.xpath('//dd[preceding-sibling::dt[contains(.,"Trạng thái")]][1]/text()').get()
        film["actors"] = response.xpath('//dd[preceding-sibling::dt[contains(.,"Đạo diễn")]][1]/a/text()').get()
        film["director"] = response.xpath('//dd[preceding-sibling::dt[contains(.,"Đạo diễn")]][1]/a/text()').get()
        film["release_year"] = response.xpath('//dd[preceding-sibling'
                                              '::dt[contains(.,"Ngày khởi chiếu")]][1]/text()').get()
        film["views"] = response.xpath('//dd[preceding-sibling::dt[contains(.,"Lượt xem")]][1]/text()').get()
        yield film
