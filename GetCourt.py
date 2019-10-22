import re
import urllib.request
import MySQL
import UrlUtil


class CourtUtil:
    # def __init__(self, database_table):

    def get_court_data(self, court_list_url, court_item_regex):
        html = UrlUtil.get_html(court_list_url)
        court_data_list = re.findall(re.compile(court_item_regex, re.S), html.decode('gbk'))
        return court_data_list

    def update_court_id(self, court_id, court_city_id, court_sub_id):
        print("start to get court list and insert into DB")
        court_info_list = self.get_court_data(court_list_url, court_item_regex)
        for court_info in court_info_list:
            if court_info.__len__() > 1:
                court_city_id = court_info[0]
                court_sub_id = court_info[1]
                court_name = court_info[2]
                auction_count = court_info[3]
                select_sql = 'select count(*) from Courts where CourtCityId="' + court_city_id + '" and CourtSubId="' + court_sub_id + '"'
                insert_sql = 'insert into Courts (CourtCityId, CourtSubId, CourtName, AuctionCount) values ("' + court_city_id + '","' + court_sub_id + '","' + court_name + '",' + auction_count + ')'
                update_sql = 'update Courts set CourtId= ' + court_id + ' where CourtCityId="' + court_city_id + '" and CourtSubId="' + court_sub_id + '"'
                mysql.upsert(select_sql, insert_sql, update_sql)
        print("end to get court list and insert into DB")

    def spider_and_upsert_court_info(self, court_list_url, court_item_regex):
        print("start to get court list and insert into DB")
        court_info_list = self.get_court_data(court_list_url, court_item_regex)
        for court_info in court_info_list:
            if court_info.__len__() > 1:
                court_city_id = court_info[0]
                court_sub_id = court_info[1]
                court_name = court_info[2]
                auction_count = court_info[3]
                select_sql = 'select count(*) from Courts where CourtCityId="' + court_city_id + '" and CourtSubId="' + court_sub_id + '"'
                insert_sql = 'insert into Courts (CourtCityId, CourtSubId, CourtName, AuctionCount) values ("' + court_city_id + '","' + court_sub_id + '","' + court_name + '",' + auction_count + ')'
                update_sql = 'update Courts set AuctionCount= ' + auction_count + ' where CourtCityId="' + court_city_id + '" and CourtSubId="' + court_sub_id + '"'
                mysql.upsert(select_sql, insert_sql, update_sql)
        print("end to get court list and insert into DB")


if __name__ == '__main__':
    mysql = MySQL.MySQL('auction_spider_ali')
    court_util = CourtUtil()
    # court_util.spider_and_upsert_court_info('https://sf.taobao.com/court_list.htm', r'<a href="\S*?\/(\d+)\/(\d+)\?\S*?" target="_blank" \S*?>(\S*?)</a>\s*<span class="iconfont-sf">\((\d+)')
    court_util.spider_and_upsert_court_info('https://sf.taobao.com/court_list.htm', r'<a href="\S*?\/(\d+)\/(\d+)\S*?" \S+>\s*(\S+)\s*</a>\s*</span>\s*<span class="iconfont-sf">\((\d+)')
    court_list = mysql.get_courts()
    print(court_list)
