# import py_stringmatching.tokenizers
# import py_stringmatching.simfunctions
from html.parser import HTMLParser

class MyHtmlParser(HTMLParser):
	# def __init__(self):
	# 	last = ""
	last = "init-value"
	def handle_data(self, data):
		# print("data !!!", data)
		value = data.strip()
		if len(value) > 0:
			if value.count(':') < 2:
				if value.count(':') == 0:
					self.last = value
				elif value[0] == ':':
					print(self.last, value)
					self.last = ""
				elif value.count(':') == 1 and value[-1] != ':':
					print(value)
					


