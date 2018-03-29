import requests
from scrapy.selector import Selector
import MySQLdb
conn = MySQLdb.connect(host="localhost",user="root",passwd="root",db="article_spider",charset="utf8")
cursor = conn.cursor()

custom_settings = {
    "COOKIES_ENABLED": False,
    "DOWNLOAD_DELAY": 1,
    'DEFAULT_REQUEST_HEADERS': {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': 'user_trace_token=20171015132411-12af3b52-3a51-466f-bfae-a98fc96b4f90; LGUID=20171015132412-13eaf40f-b169-11e7-960b-525400f775ce; SEARCH_ID=070e82cdbbc04cc8b97710c2c0159ce1; ab_test_random_num=0; X_HTTP_TOKEN=d1cf855aacf760c3965ee017e0d3eb96; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DsXIrWUxpNGLE2g_bKzlUCXPTRJMHxfCs6L20RqgCpUq%26wd%3D%26eqid%3Dee53adaf00026e940000000559e354cc; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_hotjob; login=false; unick=""; _putrc=""; JSESSIONID=ABAAABAAAFCAAEG50060B788C4EED616EB9D1BF30380575; _gat=1; _ga=GA1.2.471681568.1508045060; LGSID=20171015203008-94e1afa5-b1a4-11e7-9788-525400f775ce; LGRID=20171015204552-c792b887-b1a6-11e7-9788-525400f775ce',
        'Host': 'www.lagou.com',
        'Origin': 'https://www.lagou.com',
        'Referer': 'https://www.lagou.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    }
}

def crawl_ips():
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
    }
    for i in range(1568):

        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i),headers=headers)

        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")
        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])

            all_texts = tr.css("td::text").extract()

            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]

            ip_list.append((ip,port,proxy_type,speed))


        for ip_info in ip_list:
            sql = """
            insert into proxy_ip(ip,port,speed,proxy_type) VALUES(%s,%s,%s,%s) 
            ON DUPLICATE KEY UPDATE 
            ip=VALUES(ip)
            
            """
            params = (ip_info[0],ip_info[1],ip_info[3],ip_info[2])
            cursor.execute(sql,params)


            conn.commit()

class GetIP(object):
    def delete_ip(self,ip):
        sql = """
        delete from proxy_ip where ip='{0}'
        """.format(ip)
        cursor.execute(sql)
        conn.commit()


    def judge_ip(self,ip,port):
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip,port)
        try:
            proxy_dict = {
                "http":proxy_url
            }
            response = requests.get(http_url,proxies=proxy_dict)
        except Exception as e:
            print("invaild ip")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip")
            else:
                print("invaild ip")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        sql = """SELECT ip,port FROM proxy_ip ORDER BY RAND() LIMIT 1"""
        cursor.execute(sql)

        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]

            judge = self.judge_ip(ip,port)
            if judge:
                return "http://{0}:{1}".format(ip,port)
            else:
                return self.get_random_ip()


if __name__ == "__main__":
    #print(crawl_ips())
    get_ip = GetIP()
    get_ip.get_random_ip()