import re
import calendar
import datetime


class Parse_Imdb(object):

	def __init__(self, response):
		self.response = response
		self.regex = re.compile('(\d*,?)*\d+')

	def get_title(self):
		return self.response.xpath('//h1[@itemprop="name"]/text()').extract_first().strip()

	def get_imdb_score(self):
		imdb_score_element = self.response.xpath('//span[@itemprop="ratingValue"]/text()').extract_first()
		return float(imdb_score_element) if imdb_score_element is not None else imdb_score_element

	def get_metascore(self):
		metascore = self.response.xpath('//div[contains(@class,"metacriticScore")]/span/text()').extract_first()
		return int(metascore) if metascore is not None else metascore

	def get_genres(self):
		genres = self.response.xpath('//div[@itemprop="genre"]//a/text()').extract()
		return list(map(lambda x: x.strip(), genres))

	def get_country(self):
		country = self.response.xpath('//div[@id="titleDetails"]/div[./h4[@class="inline"][contains(text(),"Country:")]]/a/text()').extract_first()
		return country.strip()

	def get_release_date(self):
		three_letter_months = list(calendar.month_abbr)
		full_name_months = list(calendar.month_name)

		release_date = self.response.xpath('//div[@id="titleDetails"]/div[./h4[@class="inline"][contains(text(),"Release Date:")]]/text()').extract()[1].strip()
		day_raw, month_raw, year = re.search('(\d{,2})\s?([a-zA-Z]{3,}) (\d{4})', release_date).groups()

		month = three_letter_months.index(month_raw) if month_raw in three_letter_months else full_name_months.index(month_raw)
		day = int(day_raw) if day_raw is not None else 1
		return datetime.date(int(year), month, day)

	def get_budget(self):
		budget = self.response.xpath('//div[./h4[@class="inline"][contains(text(),"Budget:")]]/text()')
		return self.get_dollars(budget)

	def get_opening_usa(self):
		opening_usa = self.response.xpath('//div[./h4[@class="inline"][contains(text(),"Opening Weekend USA:")]]/text()')
		return self.get_dollars(opening_usa)

	def get_usa_gross(self):
		usa_gross = self.response.xpath('//div[./h4[@class="inline"][contains(text(),"Gross USA:")]]/text()')
		return self.get_dollars(usa_gross)

	def get_worldwide_gross(self):
		worldwide_gross = self.response.xpath('//div[./h4[@class="inline"][contains(text(),"Cumulative Worldwide Gross:")]]/text()')
		return self.get_dollars(worldwide_gross)

	def get_dollars(self, xpath):
		raw_value = xpath.extract()

		if raw_value == []:
			return None

		pattern = self.regex.search(raw_value[1].strip())

		if pattern is None:
			return None

		return int(pattern.group().replace(',', ''))
