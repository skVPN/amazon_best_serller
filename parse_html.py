# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 12:01:46 2023

@author: tim
"""

import os
import datetime
from lxml import etree
import re
import csv
import threading
from loguru import logger
import pandas as pd



class GetInfo:
    def __init__(self, root_path, download_path):

        self.root_path = root_path
        self.download_path = download_path
        self.Lock = threading.RLock()
        self.semaphore = threading.BoundedSemaphore(1)

    def html_to_str(self, asin_path):
        with open(asin_path, 'r', encoding='utf-8') as f:
            response = f.read()
        return response

    def get_info_from_asin_path_threading(self, asin_path):
        try:
            response = self.html_to_str(asin_path)
            asin = asin_path.split('\\')[-1].split('.')[0]
        except Exception as e:
            logger.info(f'获取{asin_path}的html内容失败')
            return
        # print(response)
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        try:

            # response = self.get_html_by_url(url)
            selector = etree.HTML(response)
            review_num = ''.join(
                selector.xpath('.//span[@id="acrCustomerReviewText"]/text()')[0].split(' ')[0].split(','))
        except:
            review_num = 'UNKNOWN'

        try:
            selector = etree.HTML(response)
            title = selector.xpath('//span[@id="productTitle"]/text()')[0].strip()
        except:
            title = 'UNKNOWN'

        try:
            selector = etree.HTML(response)
            # brand = selector.xpath('//a[@id="bylineInfo"]/text()')[0].strip().split('Brand: ')[1]
            brand = selector.xpath('//tr[@class="a-spacing-small po-brand"]//td[2]/span/text()')[0]
        except:
            brand = 'UNKNOWN'

        try:
            selector = etree.HTML(response)
            # price = selector.xpath('//span[@id="price_inside_buybox"]/text()')[0].strip().split('$')[1]
            # //span[@class="a-price aok-align-center"]|//span[@class="a-price a-text-price a-size-medium apexPriceToPay"]|\
            price = selector.xpath('//span[@class="a-price aok-align-center"]\
                                    /span[@class="a-offscreen"]/text()')[0].strip().split('$')[1]
            # price = selector.xpath('//span[@class="a-price aok-align-center"]/span[@class="a-offscreen"]/text()')[0].strip().split('$')[1]
        except:
            price = 'UNKNOWN'

        try:

            res_tr = r'([0-9.]+) out of 5 stars'
            review_star = float(re.findall(res_tr, response, re.S | re.M)[0])
            # selector = etree.HTML(response)
        # review_star = selector.xpath('//a[@class="a-popover-trigger a-declarative"]/span[@class="a-size-base a-color-base"]/text()')[0]
        except:
            review_star = 'UNKNOWN'

        try:
            categories = '(Amazon Devices & Accessories)(Amazon Launchpad)(Appliances)(Apps & Games)(Arts, Crafts & Sewing)\
                (Automotive)(Baby)(Beauty & Personal Care)(Books)(CDs & Vinyl)(Camera & Photo)(Cell Phones & Accessories)\
                (Clothing, Shoes & Jewelry)(Collectible Coins)(Computers & Accessories)(Digital Music)(Electronics)(Entertainment Collectibles)\
                (Gift Cards)(Grocery & Gourmet Food)(Handmade Products)(Health & Household)(Home & Kitchen)(Industrial & Scientific)(Kindle Store)\
                (Kitchen & Dining)(Magazine Subscriptions)(Movies & TV)(Musical Instruments)(Office Products)(Patio, Lawn & Garden)(Pet Supplies)\
                (Prime Pantry)(Software)(Sports & Outdoors)(Sports Collectibles)(Tools & Home Improvement)(Toys & Games)(Video Games)'

            res_tr_rank = r'#([0-9,]+) in ([{categories}]+) [(]'.format(categories=categories)
            sellers_rank, category = re.findall(res_tr_rank, response, re.S | re.M)[0]
            sellers_rank = ''.join(sellers_rank.split(','))
        except:
            sellers_rank = 'UNKNOWN'
            category = 'UNKNOWN'
        self.Lock.acquire()
        logger.info(
            f'AISI:{asin}-Title:{title}-Brand:{brand}-Price:{price}-Review_num:{review_num}-Review_star:{review_star}-Sellers_rank:{sellers_rank}-Category:{category}')
        self.Lock.release()

        result = [asin, title, brand, price, review_num, review_star, sellers_rank, category]

        if not os.path.exists(self.download_path):
            self.Lock.acquire()
            with open(download_path, 'a+') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    ['asin', 'title', 'brand', 'price', 'review_num', 'review_star', 'sellers_rank', 'category'])
            self.Lock.release()

        self.Lock.acquire()
        self.write_to_csv(self.download_path, result)
        self.Lock.release()

    def get_info_from_asin_path(self, asin_path):
        try:
            response = self.html_to_str(asin_path)
            asin = asin_path.split('\\')[-1].split('.')[0]
        except Exception as e:
            logger.info(f'获取{asin_path}的html内容失败')
            return
        # print(response)
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        try:

            # response = self.get_html_by_url(url)
            selector = etree.HTML(response)
            review_num = ''.join(
                selector.xpath('.//span[@id="acrCustomerReviewText"]/text()')[0].split(' ')[0].split(','))
        except:
            review_num = 'UNKNOWN'

        try:
            selector = etree.HTML(response)
            title = selector.xpath('//span[@id="productTitle"]/text()')[0].strip()
        except:
            title = 'UNKNOWN'

        try:
            selector = etree.HTML(response)
            # brand = selector.xpath('//a[@id="bylineInfo"]/text()')[0].strip().split('Brand: ')[1]
            brand = selector.xpath('//tr[@class="a-spacing-small po-brand"]//td[2]/span/text()')[0]
        except:
            brand = 'UNKNOWN'

        try:
            selector = etree.HTML(response)
            # price = selector.xpath('//span[@id="price_inside_buybox"]/text()')[0].strip().split('$')[1]
            # //span[@class="a-price aok-align-center"]|//span[@class="a-price a-text-price a-size-medium apexPriceToPay"]|\
            price = selector.xpath('//span[@class="a-price aok-align-center"]\
                                    /span[@class="a-offscreen"]/text()')[0].strip().split('$')[1]
            # price = selector.xpath('//span[@class="a-price aok-align-center"]/span[@class="a-offscreen"]/text()')[0].strip().split('$')[1]
        except:
            price = 'UNKNOWN'

        try:

            res_tr = r'([0-9.]+) out of 5 stars'
            review_star = float(re.findall(res_tr, response, re.S | re.M)[0])
            # selector = etree.HTML(response)
        # review_star = selector.xpath('//a[@class="a-popover-trigger a-declarative"]/span[@class="a-size-base a-color-base"]/text()')[0]
        except:
            review_star = 'UNKNOWN'

        try:
            categories = '(Amazon Devices & Accessories)(Amazon Launchpad)(Appliances)(Apps & Games)(Arts, Crafts & Sewing)\
                (Automotive)(Baby)(Beauty & Personal Care)(Books)(CDs & Vinyl)(Camera & Photo)(Cell Phones & Accessories)\
                (Clothing, Shoes & Jewelry)(Collectible Coins)(Computers & Accessories)(Digital Music)(Electronics)(Entertainment Collectibles)\
                (Gift Cards)(Grocery & Gourmet Food)(Handmade Products)(Health & Household)(Home & Kitchen)(Industrial & Scientific)(Kindle Store)\
                (Kitchen & Dining)(Magazine Subscriptions)(Movies & TV)(Musical Instruments)(Office Products)(Patio, Lawn & Garden)(Pet Supplies)\
                (Prime Pantry)(Software)(Sports & Outdoors)(Sports Collectibles)(Tools & Home Improvement)(Toys & Games)(Video Games)'

            res_tr_rank = r'#([0-9,]+) in ([{categories}]+) [(]'.format(categories=categories)
            sellers_rank, category = re.findall(res_tr_rank, response, re.S | re.M)[0]
            sellers_rank = ''.join(sellers_rank.split(','))
        except:
            sellers_rank = 'UNKNOWN'
            category = 'UNKNOWN'
        #self.Lock.acquire()
        logger.info(
            f'AISI:{asin}-Title:{title}-Brand:{brand}-Price:{price}-Review_num:{review_num}-Review_star:{review_star}-Sellers_rank:{sellers_rank}-Category:{category}')
        #self.Lock.release()

        result = [asin, title, brand, price, review_num, review_star, sellers_rank, category]

        if not os.path.exists(self.download_path):
            #self.Lock.acquire()
            with open(download_path, 'a+') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    ['asin', 'title', 'brand', 'price', 'review_num', 'review_star', 'sellers_rank', 'category'])
            #self.Lock.release()

        #self.Lock.acquire()
        self.write_to_csv(self.download_path, result)
        #self.Lock.release()


    def write_to_csv(self, download_path, content):
        with open(download_path, 'a+', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(content)

    def main_threading(self):
        all_threads = []
        asin_paths = []
        for file in os.listdir(self.root_path):
            if len(file) == 15:
                asin_path = os.path.join(self.root_path, file)
                asin_paths.append(asin_path)
        for asin_path in asin_paths:
            thread = threading.Thread(target=self.get_info_from_asin_path_threading, args=(asin_path,))
            all_threads.append(thread)

        for thread in all_threads:
            thread.start()
        for thread in all_threads:
            thread.join()

    def main(self):
        #all_threads = []
        asin_parsed = self.parsed_asin(self.download_path)
        asin_paths = []
        for file in os.listdir(self.root_path):
            if len(file) == 15:
                asin_path = os.path.join(self.root_path, file)
                asin_paths.append(asin_path)
        for asin_path in asin_paths:
            asin = asin_path.split('\\')[-1].split('.')[0]
            if asin not in asin_parsed:
                self.get_info_from_asin_path(asin_path)

    def parsed_asin(self,download_path):
        asin_data = pd.read_csv(download_path)
        asin_parsed = asin_data['asin'].drop_duplicates().tolist()
        return asin_parsed

    # def write_to_csv(self, objects, path, type='a'):
    #     with open(path, type, encoding='utf-8', newline='') as csv_file:
    #         writer = csv.writer(csv_file)
    #         writer.writerow(objects)



if __name__ == '__main__':
    root_path = 'G:\\Dropbox\\python\\amazon_best_serller\\OfficeProducts1208'
    download_path = 'G:\\OfficeProducts1208.csv'
    CollectInfo = GetInfo(root_path, download_path)
    if not os.path.exists(download_path):
        # self.Lock.acquire()
        with open(download_path, 'a+') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['asin', 'title', 'brand', 'price', 'review_num', 'review_star', 'sellers_rank', 'category'])
    #CollectInfo.main_threading()
    CollectInfo.main()
    #CollectInfo.parsed_asin(download_path)

    # for file in os.listdir(root_path):
    #    if len(file) == 15:
    #        try:
    #            asin_path =  os.path.join(root_path,file)
    #            #CollectInfo.get_info_from_asin_path(asin_path)
    #            #get_info_from_asin_path(asin_path,download_path)
    #        except Exception as e:
    #            print(e,"------------------",asin_path)
    # CollectInfo.get_info_from_asin_path('G:\\Dropbox\\python\\amazon_best_serller\\Baby0726\\B000FMQWS2.html')

































