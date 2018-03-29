
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


class Lagou(DocType):

    suggest = Completion(analyzer=ik_analyzer)
    url = Keyword()
    url_obj_id = Keyword()
    title = Text(analyzer='ik_max_word')
    min_salary = Integer()
    max_salary = Integer()
    min_work_year = Integer()
    max_work_year = Integer()
    job_city = Keyword()
    degree_need = Keyword()
    job_type = Keyword()
    publish_time = Date()
    tags = Text(analyzer='ik_max_word')
    job_advantage = Text(analyzer='ik_max_word')
    job_desc = Text(analyzer='ik_max_word')
    job_addr = Text(analyzer='ik_max_word')
    company_name = Text(analyzer='ik_max_word')


    class Meta:
        index = 'lagou'
        doc_type = 'job'
    #
    # def save(self, ** kwargs):
    #     self.lines = len(self.body.split())
    #     return super(Article, self).save(** kwargs)

    # def is_published(self):
    #     return datetime.now() < self.published_from

if __name__ == "__main__":
    Lagou().init()