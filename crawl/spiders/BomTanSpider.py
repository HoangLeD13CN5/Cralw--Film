import scrapy
from crawl.items import CrawlItem, TypeMovie
from scrapy_splash import SplashRequest


class BomTanSpider(scrapy.Spider):
    name = "bomtan"
    allowed_domains = ['bomtan.net']
    start_urls = ['http://bomtan.net/']
    script = """
           function main(splash)
               assert(splash:go(splash.args.url))
               assert(splash:wait(0.5))
               local endUrl = splash:evaljs("$('.currentpage').last().next().attr('href');")
               assert(splash:go("http://bomtan.net/" .. endUrl))
               return {
                   html = splash:html(),
                   url = splash:url(),
               }
           end
           """

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, endpoint="render.html", callback=self.parse)

    def parse(self, response):
        one_series_movie_url = response.xpath('//div[@id="menu-content"]/div/ul/'
                                              'li[contains(h3/a/@title,"Phim lẻ")]/h3')
        url = one_series_movie_url.xpath('.//a/@href').extract_first('').strip()
        item = CrawlItem()
        item['type'] = TypeMovie.oddMovies
        request = SplashRequest(response.urljoin(url), endpoint="render.html", callback=self.parse_list)
        request.meta['film'] = item
        yield request

    def start_requests_one_series_movie(self, response):
        one_series_movie_url = response.xpath('//div[@id="menu-content"]/div/ul/'
                                              'li[contains(h3/a/@title,"Phim lẻ")]/h3')
        url = one_series_movie_url.xpath('.//a/@href').extract_first('').strip()
        item = CrawlItem()
        item['type'] = TypeMovie.oddMovies
        request = SplashRequest(response.urljoin(url), endpoint="render.html", callback=self.parse_list)
        request.meta['film'] = item
        yield request

    def start_requests_many_series_movie(self, response):
        many_series_movie = '//div[@id="menu-content"]/div/ul/' \
                            'li[contains(h3/a/@title,"Phim bộ")]/div/ul/li/h3'
        for element in response.xpath(many_series_movie):
            url = element.xpath('.//a/@href').extract_first('').strip()
            item = CrawlItem()
            item['type'] = TypeMovie.suiteMovies
            request = SplashRequest(response.urljoin(url), endpoint="render.html", callback=self.parse_list)
            request.meta['film'] = item
            yield request

    def parse_list(self, response):
        film = response.meta['film'].copy()
        for element in response.xpath('//div[@class="content"]/ul[@class="movies n_list"]/li/span[@class="name"]'):
            url = element.xpath('.//a/@href').extract_first('').strip()
            request = SplashRequest(response.urljoin(url), endpoint="render.html", callback=self.parse_detail)
            request.meta['film'] = film
            yield request
        request_next_page = SplashRequest(
            url=response.url,
            callback=self.parse_list,
            meta={
                "splash": {"endpoint": "execute", "args": {"lua_source": self.script}}
            },
        )
        request_next_page.meta['film'] = film
        yield request_next_page

    def parse_detail(self, response):
        film = response.meta['film'].copy()
        film['url_root'] = self.start_urls[0]
        film["url"] = response.xpath('//p[@class="w_now"]/a[contains(text(),"xem phim")]/@href').get().strip()
        film["title"] = response.xpath('//div[@class="info_film"]/h1/text()').get().strip()
        film["title_english"] = response.xpath('//div[@class="info_film"]/h2/text()').get().strip()
        film["thumbnail"] = response.xpath('//span[@class="thumb-info"]/a/img/@src').get().strip()

        kind = ""
        for element in response.xpath('//div[@class="info_film"]/ul/'
                                      'li[contains(span/text(),"Thể loại")]/strong/a/@title'):
            kind += str(element.get()) + ","
        film["kind"] = kind[:-1]

        film["duration"] = response.xpath('//div[@class="info_film"]/ul/'
                                          'li[contains(span/text(),"Thời lượng")]/text()').get().strip()
        film["status"] = response.xpath('//div[@class="info_film"]/ul/'
                                        'li[contains(span/text(),"Trạng thái")]/span/strong/text()').get().strip()
        film["actors"] = response.xpath('//div[@class="info_film"]/ul/'
                                        'li[contains(span/text(),"Diễn viên")]/text()').get().strip()
        film["director"] = response.xpath('//div[@class="info_film"]/ul/'
                                          'li[contains(span/text(),"Đạo diễn")]/text()').get().strip()
        film["release_year"] = response.xpath('//div[@class="info_film"]/ul/'
                                              'li[contains(span/text(),"Năm phát hành")]/text()').get().strip()
        film["views"] = response.xpath('//div[@class="info_film"]/ul/'
                                       'li[contains(span/text(),"Lượt xem")]/text()').get().strip()
        film["imdb"] = response.xpath('//div[@class="info_film"]/ul/'
                                      'li[contains(span/text(),"Điểm IMDb")]/text()').get().strip()
        film["description"] = response.xpath('//div[@id="info-film"]/p/text()').get().strip()
        yield film
