# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from douban.items import DoubanItem

class Douban(CrawlSpider):
    name="douban_movie"
    url='http://movie.douban.com/top250'
    redis_key='douban:start_urls'
    start_urls=[url]

    def parse(self,response):
        item=DoubanItem()
        selector=Selector(response)
        Movies=selector.xpath('//div[@class="info"]')
        for eachMovie in Movies:
            title=eachMovie.xpath('div[@class="hd"]/a/span/text()').extract()
            fullTitle=''
            for each in title:
                fullTitle+=each
            Info=eachMovie.xpath('div[@class="bd"]/p/text()').extract()
            star=eachMovie.xpath('div[@class="bd"]/div[@class="star"]/span[@class="rating_num"]/text()').extract()[0]
            comment=eachMovie.xpath('div[@class="bd"]/div[@class="star"]/span[4]/text()').extract()[0]
            quote=eachMovie.xpath('div[@class="bd"]/p[@class="quote"]/span/text()').extract()
            quote='' if not quote else quote[0]
            #去掉多余的空格、换行
            item['title']=fullTitle.replace(' ','')
            item['Info']=';'.join(Info).replace(' ','').replace('\n','')
            item['star']=star.replace(' ','').replace('\n','')
            item['comment']=comment.replace(' ','').replace('\n','')
            item['quote']=quote.replace(' ','').replace('\n','')
            yield item

        nextLink=selector.xpath('//span[@class="next"]/link/@href').extract()
        if nextLink:
            nextLink=self.url+nextLink[0]
            yield Request(nextLink,callback=self.parse)
