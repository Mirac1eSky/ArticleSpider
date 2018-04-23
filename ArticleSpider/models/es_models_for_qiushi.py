
from datetime import datetime
from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Completion
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.analysis import CustomAnalysisDefinition
# Define a default Elasticsearch client
connections.create_connection(hosts=['localhost'])


#避免dsl报错  解决办法
class CustomAnalyzer(_CustomAnalyzer,CustomAnalysisDefinition):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer('ik_max_word',filter=['lowercase'])


class Qiushi(DocType):

    suggest = Completion(analyzer=ik_analyzer)
    url = Keyword()
    fav_nums = Keyword()
    author = Keyword()
    content = Text(analyzer='ik_max_word')


    class Meta:
        index = 'qiushi'
        doc_type = 'joke'
    #
    # def save(self, ** kwargs):
    #     self.lines = len(self.body.split())
    #     return super(Article, self).save(** kwargs)

    # def is_published(self):
    #     return datetime.now() < self.published_from

if __name__ == "__main__":
    Qiushi().init()