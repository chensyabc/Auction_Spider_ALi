from bs4 import BeautifulSoup
from lxml import etree
import re
import urllib.request
import random
import MySQL
import ssl
import time, datetime
import DateTimeUtil
import UrlUtil
from multiprocessing import Process
import ThreadUtil
import decimal
from decimal import *


class AuctionSpiderGPai:
    def get_page_total(self, total_count, each_page_count):
        page_total = total_count // each_page_count
        if total_count % each_page_count != 0:
            page_total += 1
        return page_total

    def get_total_count(self, url):
        page = UrlUtil.get_html_with_proxy(url, False)
        total_counts = re.findall(re.compile(r'<em class="count">(\d+)</em>'), page.decode('gbk'))
        return int(total_counts[0])

    def get_user_id(self, url):
        page = UrlUtil.get_html_with_proxy(url, False)
        user_id_part = re.findall(re.compile(r'<input type="hidden" name="userId" value="(\d+)"'), page.decode('gbk'))
        return user_id_part[0]

    def get_auction_json(self, url, court_id, category_id, status_id):
        auction_json = {}
        html = UrlUtil.get_html_with_proxy(url, False)
        et = etree.HTML(html)
        soup = BeautifulSoup(html, 'html.parser', from_encoding='gbk')

        auction_json['AuctionModel'] = ""
        auction_json['AuctionType'] = ""
        auction_json['SellingPeriod'] = ""
        # print(soup.find('td', class_='delay-td').find('span'))
        # print(soup.find('td', class_='delay-td').find_all('span')[1])
        auction_json['AuctionTimes'] = soup.find('td', class_='delay-td').find_all('span')[1].text[1:]
        auction_json['OnlineCycle'] = soup.find('span', class_='pay-mark').text
        auction_json['DelayCycle'] = soup.find('td', class_='delay-td').text.replace('\n', '').strip()

        auction_json['CashDeposit'] = ""
        auction_json['PaymentAdvance'] = ""

        top_info = soup.find('tbody', id='J_HoverShow')
        tds = top_info.find_all('td')

        first_line_title = tds[0].find_all('span')[0].text
        #print('first_line_title: '+ first_line_title)
        if first_line_title == '保 证 金':
            # 保 证 金: ¥500, 000            评 估 价: ¥4, 727, 500     竞价周期: 1 天
            # 起 拍 价: ¥3, 309, 250         优先购买权人: 无            延时周期: 5 分钟
            # 加价幅度: ¥5, 000
            start_price_span = tds[3].find_all('span')[2]
            cash_deposit_span = tds[0].find_all('span')[1].span
            access_price_span = tds[1].find_all('span')[1].span
            increment_span = tds[6].find_all('span')[2]
            auction_type_span = tds[2].find_all('span')[1].span
            auction_cycle_span = tds[4].find_all('span')[1].span
            prior_buyer_span = tds[5].find_all('span')[1]
        else:
            # 变卖预缴款 : ¥2,204,403.6 	加价幅度 : ¥10,000	变卖周期 : 60天
            # 保 证 金 : ¥250,000贰拾伍万元	评 估 价 : ¥2,593,416	延时周期 : 5分钟
            # 变 卖 价 : ¥2,204,403.6	优先购买权人 : 无
            start_price_span = tds[0].find_all('span')[2]
            increment_span = tds[1].find_all('span')[2]
            cash_deposit_span = tds[3].find_all('span')[1].span
            access_price_span = tds[6].find_all('span')[1].span
            auction_cycle_span = tds[4].find_all('span')[1].span
            auction_type_span = tds[2].find_all('span')[1].span
            prior_buyer_span = tds[5].find_all('span')[1]

        self.assign_auction_property(auction_json, 'StartPrice', start_price_span, True)
        self.assign_auction_property(auction_json, 'FareIncrease', increment_span, True)
        self.assign_auction_property(auction_json, 'CashDeposit', cash_deposit_span, True)
        self.assign_auction_property(auction_json, 'AccessPrice', access_price_span, True)

        auction_json['Title'] = soup.find('h1').text.replace(u"\u2022", u" ").replace(u"\xa0", u" ").strip()
        auction_json['CurrentPrice'] = soup.find('span', class_='pm-current-price').text.replace(',', '').strip()
        auction_json['CorporateAgent'] = soup.find('span', class_='item-announcement').text.strip()
        auction_json['Phone'] = soup.find('div', class_='contact-unit').find('p', class_='contact-line').find('span', class_='c-text').text
        auction_json['BiddingRecord'] = soup.find('span', class_='current-bid-user').text.strip() if soup.find('span', class_='current-bid-user') else ''
        auction_json['SetReminders'] = soup.find('span', class_='pm-reminder').find('em').text if soup.find('span', class_='pm-reminder') else 0
        auction_json['Onlookers'] = soup.find('span', class_='pm-surround').find('em').text if soup.find('span', class_='pm-surround') else 0
        auction_json['Enrollment'] = soup.find('em', class_='J_Applyer').text

        auction_json['Url'] = url
        auction_json['datetime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        auction_json['AuctionId'] = url[35:-4]
        auction_json['CourtId'] = court_id
        auction_json['CategoryId'] = category_id
        auction_json['StatusId'] = status_id
        return auction_json

    def assign_auction_property(self, auction_json, json_property, span_field, is_digital, start_index=0):
        property_value_raw = span_field.text
        if property_value_raw.__len__() != 0:
            if is_digital:
                auction_json[json_property] = Decimal(property_value_raw.replace(',', ''))
            else:
                auction_json[json_property] = property_value_raw if start_index == 0 else property_value_raw[start_index:]
        else:
            if is_digital:
                auction_json[json_property] = 0
            else:
                auction_json[json_property] = ''

    def assign_auction_property_et(self, auction_json, json_property, et, et_str, start_index=0):
        et_raw_result = et.xpath(et_str)
        auction_json[json_property] = ""
        if et_raw_result.__len__() != 0:
            et_result = et_raw_result[0]
            auction_json[json_property] = et_result if start_index == 0 else et_result[start_index:]

    def spider_auction_list_and_insert(self, url, court_id, category_id, status_id, mysql_instance, table_name):
        item_html = UrlUtil.get_html_with_proxy(url, False)
        url_partial_list = re.findall(re.compile(r'"\/\/sf-item.taobao.com\/sf_item\/(\S+.htm)'), item_html.decode('gbk'))
        for url_partial in url_partial_list:
            url = 'https://sf-item.taobao.com/sf_item/' + url_partial
            auction_json = self.get_auction_json(url, court_id, category_id, status_id)
            mysql_instance.upsert_auction(auction_json, table_name)
        return len(url_partial_list)

    def spider_auctions(self, court_list, is_auction_history, process_order, auction_processes):
        print(DateTimeUtil.get_current_time() + ThreadUtil.get_thread_id_process_order(process_order) + " Start Craw...")
        mysql_instance = MySQL.MySQL('auction_spider_ali')
        categories = mysql_instance.get_categories()
        statuses = mysql_instance.get_statuses(is_auction_history)
        count = 0
        for court_order in range(len(court_list)):
            court=court_list[court_order]
            # print('Thread Id: ' + str(threading.currentThread().ident), end='')
            # print(court)
            if int(court[4]) == 0:
                # print(court[2] + ": no auction")
                continue
            else:
                # print(court[2] + ": has auctions, start to craw")
                url_auctions_list_raw = 'https://sf.taobao.com/' + str(court[1]) + '/' + str(court[2])
                user_id = self.get_user_id(url_auctions_list_raw)
                for category in categories:
                    category_id = category[1]
                    for status in statuses:
                        if status[3] == 0:
                            continue
                        url_auctions_list = 'https://sf.taobao.com/court_item.htm?user_id=' + user_id + '&category=' + category_id + '&sorder=' + str(status[1])
                        if url_auctions_list in auction_processes:
                            print(DateTimeUtil.get_current_time() + ThreadUtil.get_thread_id_process_order(process_order) + " URL has been processed: " + url_auctions_list)
                            continue
                        mysql_instance.upsert_auction_process(url_auctions_list)
                        total_count = self.get_total_count(url_auctions_list)
                        if total_count > 0:
                            # get page count
                            each_page_count = 20
                            page_total = total_count // each_page_count
                            if total_count % each_page_count != 0:
                                page_total += 1
                            page_total = self.get_page_total(total_count, 20)
                            # process url to get html and insert
                            # print('total count: ' + str(total_count) + ' page count: ' + str(page_total))
                            for page_number in range(1, page_total + 1):
                                print(DateTimeUtil.get_current_time() + ThreadUtil.get_thread_id_process_order(process_order) + "Process Craw...", "courts " + str(court_order + 1) + "/" + str(len(court_list)) + " page " + str(page_number) + "/" + str(page_total))
                                url = url_auctions_list + '&page=' + str(page_number)
                                count += self.spider_auction_list_and_insert(url, user_id, category_id, status[1], mysql_instance, is_auction_history)
                        mysql_instance.upsert_auction_process(url_auctions_list)
        # print(court[2] + ": spider finish with count: " + str(count))
        print(DateTimeUtil.get_current_time() + "spider finish with count: " + str(count) + ThreadUtil.get_thread_id_process_order(process_order))
        print(DateTimeUtil.get_current_time() + "Finish Craw..." + ThreadUtil.get_thread_id_process_order(process_order))


if __name__ == '__main__':
    auctionSpiderGPai = AuctionSpiderGPai()
    print(DateTimeUtil.get_current_time() + " Start Main Progress--------------------------------------------------------------")
    # prepare
    print(DateTimeUtil.get_current_time(), "Get Courts Start--------------------------------------------------------------")
    mysql = MySQL.MySQL('auction_spider_ali')
    courts = mysql.get_courts()
    auction_process_all = mysql.query_auction_process_all()
    auction_processes = []
    for i in range(len(auction_process_all)):
        auction_processes.append(auction_process_all[i][1])
    print(DateTimeUtil.get_current_time(), "Get Courts End--------------------------------------------------------------")
    process_count = 100
    each_count = len(courts) // process_count
    # start multiple thread
    process_array = {}
    start_time = time.time()
    is_auction_history = False
    print(DateTimeUtil.get_current_time(), "Spider Courts Start--------------------------------------------------------------")
    for process_order in range(process_count):
        # t = Thread(target=auctionSpiderGPai.spider_auctions, args=(courts[tid:(tid+1)],))
        print(DateTimeUtil.get_current_time() + ' Process Order-' + str(process_order), 'court count: ' + str(len(courts[process_order * each_count:(process_order + 1) * each_count])) + " court list: below")
        print(courts[process_order * each_count:(process_order + 1) * each_count])
        t = Process(target=auctionSpiderGPai.spider_auctions, args=(courts[process_order * each_count:(process_order + 1) * each_count], is_auction_history, str(process_order), auction_processes,))
        t.start()
        process_array[process_order] = t
    for i in range(process_count):
        process_array[i].join()
    end_time = time.time()
    print(DateTimeUtil.get_current_time(), "Spider Courts End--------------------------------------------------------------")
    print(DateTimeUtil.get_current_time(), "Total time: {}".format(end_time - start_time))
    print(DateTimeUtil.get_current_time(), "End Main Progress--------------------------------------------------------------")
