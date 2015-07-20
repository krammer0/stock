# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import urllib                                       
from re import sub
from decimal import Decimal
from bs4 import BeautifulSoup as Soup 
from operator import itemgetter, attrgetter
from datetime import datetime, timedelta

FETCH_DAY = 60
CLOSE_FIRST = 0
LOW_FIRST = 1
google_url = "https://www.google.com/finance/historical?q=TPE:"
google_url1 = "&num="

class DayData:  
    def __init__(self):
        self.data = ""
        self.start = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.volume = 0
        self.day_num = 0
    def set_date(self, date):
        self.date = date
    def set_start(self, start):
        try:
            float_num = float(start.replace(',',''))
            self.start = float_num
            return 0
        except ValueError:
            return -1
    def set_high(self, high):
        try:
            float_num = float(high.replace(',',''))
            self.high = float_num
            return 0
        except ValueError:
            return -1
    def set_low(self, low):
        try:
            float_num = float(low.replace(',',''))
            self.low = float_num
            return 0
        except ValueError:
            return -1
    def set_close(self, close):
        try:
            float_num = float(close.replace(',',''))
            self.close = float_num
            return 0
        except ValueError:
            return -1
    def set_volume(self, volume):
        self.volume = volume
    def set_day_num(self, num):
        self.day_num = num

class Stock:
    def __init__(self, url, name):
        token = name.split()
        self.stock_name = name
        self.stock_num = token[0]
        self.day_data = []
        #self.sorted_data = []
        self.fetch_data(url)
    def add_data(self, data):
        self.day_data.append(data)
    def fetch_data(self, url):
        i = 0
        day_num = 1
        skip_this_one = 0
        number_of_elements = 6
        sock = urllib.urlopen(url) 
        htmlSource = sock.read()                            
        sock.close()                                        
        tmp_day_data = DayData()

        soup = Soup(htmlSource, "html.parser")
        #print soup
        historical_table_tag = soup.select(".historical_price")
        for td in historical_table_tag[0].find_all("td"):
            mod = i % number_of_elements
            #print td.contents[0]
            if mod == 0:
                if skip_this_one == 0:
                    tmp_day_data.set_date(td.contents[0])
            elif mod == 1:
                if skip_this_one == 0:
                    skip_this_one = tmp_day_data.set_start(td.contents[0])
            elif mod == 2:
                if skip_this_one == 0:
                    skip_this_one = tmp_day_data.set_high(td.contents[0])
            elif mod == 3:
                if skip_this_one == 0:
                    skip_this_one = tmp_day_data.set_low(td.contents[0])
            elif mod == 4:
                if skip_this_one == 0:
                    skip_this_one = tmp_day_data.set_close(td.contents[0])
            elif mod == 5:
                if skip_this_one == 0:
                    tmp_day_data.set_volume(Decimal(sub(r'[^\d.]', '', td.contents[0])))
                    tmp_day_data.set_day_num(day_num)
                    self.add_data(tmp_day_data)
                    tmp_day_data = DayData()
                    day_num = day_num + 1
                else:
                    skip_this_one = 0
            i = i + 1
    def print_all_data(self):
        print len(self.day_data)
        for data in self.day_data:
            print "=================="
            print "date " + data.date
            print data.start
            print data.high
            print data.low
            print data.close
            print data.volume
            print data.day_num
    def lowest_data(self, left_idx, right_idx, which):#left is larger than right, because the latest day_num is 1
        #if len(self.sorted_data) == 0:
        #    self.sorted_data = sorted(self.day_data, key=attrgetter('close', 'low'))
        if left_idx < right_idx:
            return None
        if which == 0:
            sorted_data = sorted(self.day_data[right_idx:left_idx], key=attrgetter('close', 'low'))
        elif which == 1:
            sorted_data = sorted(self.day_data[right_idx:left_idx], key=attrgetter('low', 'close'))
        #for data in sorted_data:
        #    print data.date + " " + str(data.close)
        return sorted_data[0]
    def highest_data(self, left_idx, right_idx, which):
        if left_idx < right_idx:
            return None
        if which == 0:
            sorted_data = sorted(self.day_data[right_idx:left_idx], key=attrgetter('close', 'high'), reverse=True)
        elif which == 1:
            sorted_data = sorted(self.day_data[right_idx:left_idx], key=attrgetter('high', 'close'), reverse=True)
        return sorted_data[0]

class StockFinder:
    def __init__(self):
        self.all_stock_list = []
    def sync_all_stock_list_from_internet(self):
        i = 0
        file = open('all_stock.txt', 'w')
        sock = urllib.urlopen("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2") 
        htmlSource = sock.read().decode("big5", 'ignore')                            
        sock.close()
        soup = Soup(htmlSource, "html.parser")
        all_td = soup.select("td")
        for td in all_td:
            if len(td.contents) < 1:
                #print "no content?"
                continue
            #print td.contents[0]
            #print type(td.contents[0])
            if hasattr(td.contents[0], 'children'):
                #print "td contents not a str"
                continue

            token = td.contents[0].split()
            #expect like this: 2330 TSMC
            if len(token) != 2:
                #print "token != 2"
                continue
            if token[0].isdigit() == False:
                #print "not digit"
                continue
            if int(token[0]) > 9999:
                print "return"
                break
            i = i + 1
            #print td.contents[0]
            file.write(td.contents[0] + "         " + str(i) + "\n")
        file.close()
    def prepare_all_stock_list(self):
        file = open('all_stock.txt', 'r')
        line = file.readline()
        while line != '':
            #token = line.split()
            #self.all_stock_list.append(token[0])
            self.all_stock_list.append(line)
            line = file.readline()
        #for stock_num in self.all_stock_list:
        #    print stock_num
    def algo0(self, stock, file):
    	if FETCH_DAY < 60:
		print 'cant run 3 month ago data'
        #print stock.lowest_data(fetch_day, 1).date.rstrip()
        3rd_month_lowest_data = stock.lowest_data(59, 40, CLOSE_FIRST)
        #print lowest_data.date.rstrip()
        1st_month_lowest_data = stock.lowest_data(19, 0, CLOSE_FIRST)
        if 3rd_month_lowest_data.close < 1st_month_lowest_data.close:
            print stock.stock_name
            print 3rd_month_lowest_data.date.rstrip()
            print 1st_month_lowest_data.date.rstrip()
            file.write("<a href=\"http://www.cmoney.tw/finance/f00025.aspx?s=" + stock.stock_num + "\">" + stock.stock_name + "</a><br>\n")
    def algo1(self, stock, file):
       #print stock.lowest_data(fetch_day, 1).date.rstrip()
        lowest_data = stock.lowest_data(len(stock.day_data) - 1, 0, LOW_FIRST)
        #print lowest_data.date.rstrip()
        if lowest_data.day_num >= 185 and lowest_data.day_num <= 215:
            print stock.stock_name
            print lowest_data.date.rstrip()
            #file.write(stock.stock_name + " ==> http://www.cmoney.tw/finance/f00025.aspx?s=" + stock.stock_num + "\n")
            file.write("<a href=\"http://www.cmoney.tw/finance/f00025.aspx?s=" + stock.stock_num + "\">" + stock.stock_name + "</a><br>\n")
            
    def find_stock(self, algo, start, end):
        now = datetime.now()
        self.prepare_all_stock_list()
        if algo == 99:#test case
            file = open('test.txt', 'w')
            stock_num = 4532 
            file.write("process ======== " + str(stock_num))
            stock = Stock(google_url + str(stock_num) + google_url1 + str(FETCH_DAY), stock_num)
            #stock.print_all_data()
            self.algo0(stock, file)
            file.close()
        if algo == 0:
            file_name = "algo0_" + now.strftime("%Y-%m-%d") + ".html"
            file = open(file_name, 'w')
            for line in self.all_stock_list:
                #print "===================="
                #print type(stock_num)
                token = line.split()
                stock_num = token[0]
                if int(stock_num) == 8150:#no data in google finace...
                    continue
                if int(stock_num) < start or int(stock_num) > end:
                    continue
                #file.write("process ======== " + str(stock_num))
                stock = Stock(google_url + str(stock_num) + google_url1 + str(FETCH_DAY), token[0] + " " + token[1])
                self.algo0(stock, file)
                #file.write("\n")
            file.close()
        if algo == 1:
            FETCH_DAY = 300
            file_name = "algo1_" + now.strftime("%Y-%m-%d") + ".html"
            file = open(file_name, 'w')
            for line in self.all_stock_list:
                token = line.decode('utf-8').split()
                stock_num = token[0]
                #print stock_num
                if int(stock_num) == 8150:#no data in google finace
                    continue
                if int(stock_num) < start or int(stock_num) > end:
                    continue
                #file.write("process ======== " + str(stock_num))
                stock = Stock(google_url + str(stock_num) + google_url1 + str(FETCH_DAY), token[0] + " " + token[1])
                self.algo1(stock, file)
                #file.write("\n")
            file.close()


#url = "https://www.google.com/finance/historical?q=TPE:3617&num=80"
#this_stock = Stock(url, 3617)
stock_finder = StockFinder()

#stock_finder.sync_all_stock_list_from_internet()
#this_stock.fetch_data(url)
#this_stock.print_all_data()
#lowest_data = this_stock.lowest_data(80, 1)
#print lowest_data.date.rstrip()
#next_lowest_data = this_stock.lowest_data(lowest_data.day_num - 10, 1)
#print next_lowest_data.date.rstrip()
#print this_stock.second_lowest_price()
#stock_finder.prepare_all_stock_list()
stock_finder.find_stock(1, 0, 9999)
#stock_finder.find_all_stock(99)
