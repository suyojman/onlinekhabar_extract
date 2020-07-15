import scrapy
from newscraper.items import NewscraperItem
from scrapy.exceptions import DropItem,CloseSpider
from newscraper.models import News
from sqlalchemy.orm import sessionmaker

class QuoteSpider(scrapy.Spider):
    name = 'onlinekhabar'
    start_urls = ['https://www.onlinekhabar.com/content/news']
    close_manually = False
    skip_on_title_match = True
    stop_on_title_match = True
    page_number_limit = '3'

    def parse(self, response):
        # news_sections={
        #     'main':'//a[contains(@class, "title__regular")]',
        #     'secondary:'//a[contains(@class, "title__regular")]'
        # }
        
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
            yield response.follow(news_link,self.parse_details, meta={'news_item':news_item})
            
        next_page = str(current_page + 1)
        if self.close_manually:
            yield scrapy.Request(news_link, callback=self.close_spider)
            # raise CloseSpider("Duplicate News")
        elif next_page==self.page_number_limit:
            yield scrapy.Request(news_link, callback=self.close_spider)
        elif next_page is not None:
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

    def close_spider(self,response):
        return None
        # raise CloseSpider("Page Number limit reached")

       
            