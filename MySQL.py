import MySQLdb
import DateTimeUtil
import threading


class MySQL:
    def __init__(self, database_table):
        try:
            print(DateTimeUtil.get_current_time(), "Start Connection DB...")
            self.db = MySQLdb.connect('localhost', 'root', 'chensy123', database_table, 3306)
            self.cur = self.db.cursor()
            print(DateTimeUtil.get_current_time(), "Connection DB Successful...", str(threading.currentThread().ident))
        except MySQLdb.Error as e:
            print(DateTimeUtil.get_current_time(), "Connection DB Failure: %d: %s" % (e.args[0], e.args[1]), str(threading.currentThread().ident))

    def get_courts(self, is_filter_count=True):
        if is_filter_count:
            sql_select = "select Id, CourtCityId, CourtSubId, CourtName, AuctionCount from Courts WHERE AuctionCount > 0"
        else:
            sql_select = "select Id, CourtCityId, CourtSubId, CourtName, AuctionCount from Courts"
        return self.select(sql_select)

    def get_categories(self):
        sql_select = "SELECT Id, CategoryId, CategoryName FROM Auction_Categories"
        return self.select(sql_select)

    def get_statuses(self, is_auction_history):
        table_name = 'Auction_History_Statuses' if is_auction_history else 'Auction_Statuses'
        sql_select = 'SELECT Id, StatusId, StatusName, IsSpiderThisStatus FROM ' + table_name
        return self.select(sql_select)

    def select(self, select_sql):
        try:
            self.db.set_character_set('utf8')
            self.cur.execute(select_sql)
            return list(self.cur._rows)
        except MySQLdb.Error as e:
            print(DateTimeUtil.get_current_time(), "DB Select Failure: %d: %s" % (e.args[0], e.args[1]))
        except Exception as ex:
            print(DateTimeUtil.get_current_time(), "DB Select Failure: %d: %s" % (e.args[0], e.args[1]))

    def upsert(self, insert_sql_check, insert_sql, update_sql):
        try:
            self.db.set_character_set('gbk')
            self.cur.execute(insert_sql_check)
            if self.cur._rows[0][0] == 0:
                try:
                    result = self.cur.execute(insert_sql)
                    insert_id = self.db.insert_id()
                    self.db.commit()
                    if result:
                        return insert_id
                    else:
                        return 0
                except MySQLdb.Error as e:
                    self.db.rollback()
                    if "key 'PRIMARY'" in e.args[1]:
                        print(DateTimeUtil.get_current_time(), "Primary Key Exists")
                    else:
                        print(DateTimeUtil.get_current_time(), "Insert Failure: %d: %s" % (e.args[0], e.args[1]))
                        exit()
            else:
                result = self.cur.execute(update_sql)
                insert_id = self.db.insert_id()
                self.db.commit()
                if result:
                    return insert_id
                else:
                    return 0
        except MySQLdb.Error as e:
            print(DateTimeUtil.get_current_time(), "Upsert Failure: %d: %s" % (e.args[0], e.args[1]))
            exit()
        except Exception as ex:
            print(DateTimeUtil.get_current_time(), "DB Object Error: %d: %s" % (ex.args[0], ex.args[1]))

    def upsert_auction(self, auction_json, is_auction_history):
        table_name = 'Auctions_History' if is_auction_history else 'Auctions'
        insert_check = 'SELECT COUNT(*) FROM ' + table_name + ' WHERE AuctionId = ' + auction_json['AuctionId']
        insert_sql = "INSERT INTO %s (%s) VALUES (%s)" % (table_name,
                                                          "AuctionId,CourtId,Title,CategoryId,Url,StartPrice,CurrentPrice,CashDeposit,PaymentAdvance,AccessPrice,FareIncrease,AuctionTimes,AuctionType,DelayCycle,CorporateAgent,Phone,SellingPeriod,OnlineCycle,BiddingRecord,AuctionModel,Enrollment,SetReminders,Onlookers,CreatedOn,StatusId,SpiderStatusId",
                                                          str(auction_json['AuctionId']) + ",'" + str(
                                                              auction_json['CourtId']) + "','" + str(
                                                              auction_json['Title']) + "','" + str(
                                                              auction_json['CategoryId']) + "','" + str(
                                                              auction_json['Url']) + "','" + str(
                                                              auction_json['StartPrice']) + "','" + str(
                                                              auction_json['CurrentPrice']) + "','" + str(
                                                              auction_json['CashDeposit']) + "','" + str(
                                                              auction_json['PaymentAdvance']) + "','" + str(
                                                              auction_json['AccessPrice']) + "','" + str(
                                                              auction_json['FareIncrease']) + "','" + str(
                                                              auction_json['AuctionTimes']) + "','" + str(
                                                              auction_json['AuctionType']) + "','" + str(
                                                              auction_json['DelayCycle']) + "','" + str(
                                                              auction_json['CorporateAgent']) + "','" + str(
                                                              auction_json['Phone']) + "','" + str(
                                                              auction_json['SellingPeriod']) + "','" + str(
                                                              auction_json['OnlineCycle']) + "','" + str(
                                                              auction_json['BiddingRecord']) + "','" + str(
                                                              auction_json['AuctionModel']) + "','" + str(
                                                              auction_json['Enrollment']) + "','" + str(
                                                              auction_json['SetReminders']) + "','" + str(
                                                              auction_json['Onlookers']) + "','" + str(
                                                              auction_json['datetime']) + "','" + str(
                                                              auction_json['StatusId']) + "','1'")
        update_sql = 'UPDATE ' + table_name + ' SET ' \
                     + 'CourtId=' + str(auction_json['CourtId']) \
                     + ',Title="' + str(auction_json['Title']) \
                     + '",CategoryId=' + str(auction_json['CategoryId'])\
                     + ',Url="' + str(auction_json['Url'])\
                     + '",StartPrice=' + str(auction_json['StartPrice'])\
                     + ',CurrentPrice="' + str(auction_json['CurrentPrice'])\
                     + '",CashDeposit="' + str(auction_json['CashDeposit'])\
                     + '",PaymentAdvance="' + str(auction_json['PaymentAdvance'])\
                     + '",AccessPrice="' + str(auction_json['AccessPrice'])\
                     + '",FareIncrease="' + str(auction_json['FareIncrease'])\
                     + '",AuctionTimes="' + str(auction_json['AuctionTimes']) \
                     + '",AuctionType="' + str(auction_json['AuctionType'])\
                     + '",DelayCycle="' + str(auction_json['DelayCycle'])\
                     + '",CorporateAgent="' + str(auction_json['CorporateAgent'])\
                     + '",Phone="' + str(auction_json['Phone'])\
                     + '",SellingPeriod="' + str(auction_json['SellingPeriod'])\
                     + '",SetReminders="' + str(auction_json['SetReminders'])\
                     + '",OnlineCycle="' + str(auction_json['OnlineCycle'])\
                     + '",BiddingRecord="' + str(auction_json['BiddingRecord'])\
                     + '",AuctionModel="' + str(auction_json['AuctionModel'])\
                     + '",Enrollment="' + str(auction_json['Enrollment'])\
                     + '",SetReminders="' + str(auction_json['SetReminders'])\
                     + '",Onlookers="' + str(auction_json['Onlookers'])\
                     + '",UpdatedOn="' + str(auction_json['datetime'])\
                     + '",StatusId=' + str(auction_json['StatusId'])\
                     + ',SpiderStatusId=2 WHERE AuctionId=' + str(auction_json['AuctionId'])
        self.upsert(insert_check, insert_sql, update_sql)

# if __name__ == '__main__':
#     mysql = Mysql()
#     court_list = mysql.getCourtList()
#     for court in court_list:
#         print(court[2] + "," + str(court[0]) + "," + str(court[1]))
