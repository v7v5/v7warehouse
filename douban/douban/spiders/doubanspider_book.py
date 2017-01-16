# -*- coding: utf-8 -*-
from v7 import *
import unicodedata
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from douban.items import DoubanItem

def rmSpc(*STRING):
    return (str(s).replace(' ','').replace('\n','') for s in STRING) if len(STRING)>1 \
        else str(*STRING).replace(' ','').replace('\n','') 

class Douban(CrawlSpider):
    name="douban_book"
    url='http://book.douban.com/top250'
    redis_key='douban:start_urls'
    start_urls=[url]       

    def parse(self,response):
        item=DoubanItem()
        selector=Selector(response)

        Books=selector.xpath('//tr[@class="item"]/td[2]')
        for eachBook in Books:
            title_tmp=eachBook.xpath('div[1]//text()').extract()
            title=''
            for i in title_tmp:
                title+=unicodedata.normalize("NFKD", i)             #去除奇怪的编码格式如/xa0
            Info=eachBook.xpath('p[1]//text()').extract()[0]
            star=eachBook.xpath('div[2]/span[2]//text()').extract()[0]
            comment=eachBook.xpath('div[2]/span[3]//text()').extract()[0]
            quote=eachBook.xpath('p[2]/span//text()').extract()
            quote='' if not quote else quote[0]
            #去掉多余的空格、换行
            item['title'],item['Info'],item['star'],item['comment'],item['quote']=rmSpc(title,Info,star,comment,quote)
            yield item

        nextLink=selector.xpath('//span[@class="next"]/link/@href').extract()
        if nextLink:
            nextLink=nextLink[0]
            yield Request(nextLink,callback=self.parse)
