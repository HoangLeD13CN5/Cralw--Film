import scrapy
from crawl.items import CrawlItem, TypeMovie
from scrapy_splash import SplashRequest


class BomTanSpider(scrapy.Spider):
    name = "bomtan"
    allowed_domains = ['bomtan.net']
    start_urls = ['http://bomtan.net/']
    is_cralw_all = False
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

        many_series_movie = response.xpath('//div[@id="menu-content"]/div/ul/li[contains(h3/a/@title,"Phim bộ")]/h3')
        many_series_movie_url = many_series_movie.xpath('.//a/@href').extract_first('').strip()
        item_suite = CrawlItem()
        item_suite['type'] = TypeMovie.suiteMovies
        request_suite = SplashRequest(response.urljoin(many_series_movie_url), endpoint="render.html", callback=self.parse_list)
        request_suite.meta['film'] = item_suite
        yield request_suite

    def parse_list(self, response):
        film = response.meta['film'].copy()
        for element in response.xpath('//div[@class="content"]/ul[@class="movies n_list"]/li/span[@class="name"]'):
            url = element.xpath('.//a/@href').extract_first('').strip()
            request = SplashRequest(response.urljoin(url), endpoint="render.html", callback=self.parse_detail)
            request.meta['film'] = film
            yield request
        if self.is_cralw_all:
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
        film["url"] = response.xpath('//p[@class="w_now"]/a[contains(text(),"xem phim")]/@href').get()
        film["title"] = response.xpath('//div[@class="info_film"]/h1/text()').get()
        film["title_english"] = response.xpath('//div[@class="info_film"]/h2/text()').get()
        film["thumbnail"] = response.xpath('//span[@class="thumb-info"]/a/img/@src').get()

        kind = ""
        for element in response.xpath('//div[@class="info_film"]/ul/'
                                      'li[contains(span/text(),"Thể loại")]/strong/a/@title'):
            kind += str(element.get()) + ","
        film["kind"] = kind[:-1]

        film["duration"] = response.xpath('//div[@class="info_film"]/ul/'
                                          'li[contains(span/text(),"Thời lượng")]/text()').get()
        film["status"] = response.xpath('//div[@class="info_film"]/ul/'
                                        'li[contains(span/text(),"Trạng thái")]/span/strong/text()').get()
        film["actors"] = response.xpath('//div[@class="info_film"]/ul/'
                                        'li[contains(span/text(),"Diễn viên")]/text()').get()
        film["director"] = response.xpath('//div[@class="info_film"]/ul/'
                                          'li[contains(span/text(),"Đạo diễn")]/text()').get()
        film["release_year"] = response.xpath('//div[@class="info_film"]/ul/'
                                              'li[contains(span/text(),"Năm phát hành")]/text()').get()
        film["views"] = response.xpath('//div[@class="info_film"]/ul/'
                                       'li[contains(span/text(),"Lượt xem")]/text()').get()
        film["imdb"] = response.xpath('//div[@class="info_film"]/ul/'
                                      'li[contains(span/text(),"Điểm IMDb")]/text()').get()
        film["description"] = response.xpath('//div[@id="info-film"]/p/text()').extract_first('').strip()
        yield film
