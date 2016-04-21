# import py_stringmatching.tokenizers
# import py_stringmatching.simfunctionse
from html.parser import HTMLParser

class MyHtmlParser(HTMLParser):
    last = "init-value"
    result = {}

    def handle_data(self, data):
        value = data.strip()
        if len(value) > 0:
            if value.count(':') < 2:
                if value.count(':') == 0:
                    self.last = value
                elif value[0] == ':':
                    value = value[1:].strip()
                    if len(self.last) < 50:
                        self.result[self.last] = value
                    self.last = ""
                elif value.count(':') == 1 and value[-1] != ':':
                    split = value.split(':', 1)
                    if len(split[0].strip()) < 50:
                        self.result[split[0].strip()] = split[1].strip()



