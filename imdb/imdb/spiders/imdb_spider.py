from scrapy import Request, Spider
from imdb.items import ImdbItem
import re
import calendar
import datetime


class ImdbSpider(Spider):

	name = 'imdb_spider'
	allowed_url = ['https://www.imdb.com/']
	start_urls = ['https://www.imdb.com/search/title?year=2015&title_type=feature&view=simple&page=1&ref_=adv_nxt']

	def parse(self, response):

		for year in range(2015, 2016):

			# get number of pages and total pages for that year
			regex = re.compile('of (\d*,?\d+)')
			text = response.xpath('//div[@class="desc"]/text()').extract()
			filtered_text = list(filter(regex.search, text))[0]
			total_num = int(regex.search(filtered_text).group(1).replace(',', ''))
			num_per_page = int(response.xpath('//span[@class="lister-current-last-item"]/text()').extract_first())
			total_pages = total_num // num_per_page + 1
			# total_pages = 1

			base_url = 'https://www.imdb.com/search/title?year={year}&title_type=feature&view=simple&page={page}&ref_=adv_nxt'
			list_urls = [base_url.format(year=year, page=x) for x in range(1, total_pages + 1)]

			for url in list_urls:
				yield Request(url, callback=self.parse_result_page)

	def parse_result_page(self, response):

		movies = response.xpath('//span[@class="lister-item-header"]//a/@href').extract()
		movie_urls = ['https://www.imdb.com' + x for x in movies]

		for url in movie_urls:
			yield Request(url, callback=self.parse_movie_page)

	def get_gross(self, regex, xpath):
		try:
			return int(regex.search(xpath.extract()[1].strip()).group().replace(',', ''))
		except IndexError:
			pass

	def parse_movie_page(self, response):

		title = response.xpath('//h1[@itemprop="name"]/text()').extract_first().strip()
		imdb_score = float(response.xpath('//span[@itemprop="ratingValue"]/text()').extract_first())
		metascore = 0
		try:
			metascore = int(response.xpath('//div[contains(@class,"metacriticScore")]/span/text()').extract_first())
		except TypeError:
			pass
		genres = list(map(lambda x: x.strip(), response.xpath('//div[@itemprop="genre"]//a/text()').extract()))
		country = response.xpath('//div[@id="titleDetails"]/div[./h4[@class="inline"][contains(text(),"Country:")]]/a/text()').extract_first()

		regex = re.compile('(\d{1,2}) ([a-zA-Z]{3,}) (\d{4})')
		release_date_raw = list(filter(regex.search, response.xpath('//div[@id="titleDetails"]/div[./h4[@class="inline"][contains(text(),"Release Date:")]]/text()').extract()))[0].strip()
		day, month_raw, year = regex.search(release_date_raw).groups()
		three_letter_months = list(calendar.month_abbr)
		month_int = three_letter_months.index(month_raw) if month_raw in three_letter_months else list(calendar.month_name).index(month_raw)
		release_date = datetime.date(int(year), month_int, int(day))

		regex = re.compile('(\d*,?)*\d+')

		budget_raw = response.xpath('//div[./h4[@class="inline"][contains(text(),"Budget:")]]/text()')
		budget = self.get_gross(regex, budget_raw)

		opening_usa_raw = response.xpath('//div[./h4[@class="inline"][contains(text(),"Opening Weekend USA:")]]/text()')
		opening_usa = self.get_gross(regex, opening_usa_raw)

		usa_gross_raw = response.xpath('//div[./h4[@class="inline"][contains(text(),"Gross USA:")]]/text()')
		usa_gross = self.get_gross(regex, usa_gross_raw)

		worldwide_gross_raw = response.xpath('//div[./h4[@class="inline"][contains(text(),"Cumulative Worldwide Gross:")]]/text()')
		worldwide_gross = self.get_gross(regex, worldwide_gross_raw)

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
