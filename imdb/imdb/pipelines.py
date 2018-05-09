# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonLinesItemExporter


class WriteImdbPipeline(object):

	def __init__(self):
		self.filename = 'imdb.json'

	def open_spider(self, spider):
		self.jsonfile = open(self.filename, 'wb')
		self.exporter = JsonLinesItemExporter(self.jsonfile)
		self.exporter.start_exporting()

	def close_spider(self, spider):
		self.exporter.finish_exporting()
		self.jsonfile.close()

	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item
