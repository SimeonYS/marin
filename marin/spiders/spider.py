import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import MarinItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class MarinSpider(scrapy.Spider):
	name = 'marin'
	start_urls = ['https://www.bankofmarin.com/about-us/news/press-release-archive/']

	def parse(self, response):
		articles = response.xpath('//li[contains(@class,"page_item page-item-")]')
		for article in articles:
			date = article.xpath('./text()').get().strip()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="main"]//text()[not(ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=MarinItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
