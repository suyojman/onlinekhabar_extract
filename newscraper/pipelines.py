# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem,CloseSpider
from newscraper.models import News, db_connect, create_table
import logging

class NewscraperPipeline(object):
    
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        news = News()
        news.title = item['title']
        news.link = item['link']
        news.published_date = item['published_date']
        news.details = item['details']
        try:
            session.add(news)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()
        return item

class DuplicatesPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates tables.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        logging.info("****DuplicatesPipeline: database connected****")

    def process_item(self, item, spider):
        session = self.Session()
        exist_title = session.query(News).filter_by(title = item['title']).first()
        if exist_title is not None:
            print('>>>>>>>', exist_title.id, exist_title.title)
            self.close_spider(spider)
            raise DropItem("Dublicate item found: %s" %item['title'])
            
            session.close()
        else:
            return item
            session.close()

    def close_spider(self, spider):
        spider.close_manually = True