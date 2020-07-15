import scrapy
from newscraper.items import NewscraperItem
from scrapy.exceptions import DropItem,CloseSpider
from newscraper.models import News
from sqlalchemy.orm import sessionmaker

class QuoteSpider(scrapy.Spider):
    name = 'onlinekhabar'
    start_urls = ['https://www.onlinekhabar.com/content/news']
    close_manually = False

    def parse(self, response):
        links = response.xpath('//a[contains(@class, "title__regular")]')
        current_page = int(response.xpath('//span[contains(@class, "page-numbers current")]').css('span::text').get())
        for news in links:
            news_item = NewscraperItem()
            news_title = news.css('a::text').get()
            news_link = news.xpath('@href').get()
            data = {'title' : news_title,
                    'link' : news_link}
            news_item['title'] = news_title
            news_item['link'] = news_link
            if self.close_manually:
                raise CloseSpider("Dublicate News")
            yield response.follow(news_link,self.parse_details, meta={'news_item':news_item})
            
           
            
        next_page = str(current_page + 1)
        if next_page is not None:
            next_page_link = 'https://www.onlinekhabar.com/content/news/page/' + next_page
            yield scrapy.Request(next_page_link, callback=self.parse)

    def parse_details(self, response):
        news_item = response.meta['news_item']
        date_selection = response.xpath("//div[contains(@class, 'post__time')]")
        details = response.xpath("//div[contains(@class, 'main__read--content')]")
        published_date = date_selection.css('span::text').get()
        news_details = ''.join(details.css('p::text').getall())
        news_item['published_date'] = published_date
        news_item['details'] = news_details
        data = {'date_published':published_date,
                'news_details':news_details}
        yield news_item

       
            