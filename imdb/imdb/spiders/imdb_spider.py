from scrapy import Request, Spider
from imdb.items import ImdbItem
from imdb.parse_imdb import Parse_Imdb
import re


class ImdbSpider(Spider):

	name = 'imdb_spider'
	allowed_url = ['https://www.imdb.com/']
	start_urls = ['https://www.imdb.com/search/title?year=2015&title_type=feature&view=simple&page=1&ref_=adv_nxt']

	def parse(self, response):

		for year in range(2015, 2016):

			# get number of pages and total pages for that year
			regex = re.compile('of (\d*,?\d+)')
			text = response.xpath('//div[@class="desc"]/text()').extract()[2]
			total_num = int(regex.search(text).group(1).replace(',', ''))
			num_per_page = int(response.xpath('//span[@class="lister-current-last-item"]/text()').extract_first())
			total_pages = total_num // num_per_page + 1
			total_pages = 3

			base_url = 'https://www.imdb.com/search/title?year={year}&title_type=feature&view=simple&page={page}&ref_=adv_nxt'
			list_urls = [base_url.format(year=year, page=x) for x in range(1, total_pages + 1)]

			for url in list_urls[:5]:
				yield Request(url, callback=self.parse_result_page)

	def parse_result_page(self, response):

		movies = response.xpath('//span[@class="lister-item-header"]//a/@href').extract()
		movie_urls = ['https://www.imdb.com' + x for x in movies]

		for url in movie_urls:
			yield Request(url, callback=self.parse_movie_page)

	def parse_movie_page(self, response):

		parse = Parse_Imdb(response)
		title = parse.get_title()
		imdb_score = parse.get_imdb_score()
		metascore = parse.get_metascore()
		genres = parse.get_genres()
		country = parse.get_country()
		release_date = parse.get_release_date()
		budget = parse.get_budget()
		opening_usa = parse.get_opening_usa()
		usa_gross = parse.get_usa_gross()
		worldwide_gross = parse.get_worldwide_gross()

		root_url = response.request.url.split('/')[:-1]
		root_url.append('companycredits?ref_=tt_dt_co')
		url_companies = '/'.join(root_url)

		item = ImdbItem()
		item['title'] = title
		item['imdb_score'] = imdb_score
		item['metascore'] = metascore
		item['genres'] = genres
		item['country'] = country
		item['release_date'] = release_date
		item['budget'] = budget
		item['opening_usa'] = opening_usa
		item['usa_gross'] = usa_gross
		item['worldwide_gross'] = worldwide_gross

		yield Request(url_companies, callback=self.parse_companies, meta={'imdb_item': item})

	def parse_companies(self, response):

		item = response.meta['imdb_item']
		companies = list(map(lambda x: x.strip(), response.xpath('//div[@id="company_credits_content"]/ul[1]//a/text()').extract()))
		item['production_companies'] = companies

		yield item
