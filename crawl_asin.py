from crawl_category_all import AmazonCrawler
import json

if __name__ == "__main__":
    # a=AmazonCrawler()
    url_crawled_path = 'G:\\Dropbox\\python\\amazon_best_serller\\Baby1222\\url_crawled.txt'
    url_crawled = []
    with open(url_crawled_path, 'rb+') as txt_file:
        for eachline in txt_file.readlines():
            result = eachline.decode().replace("\n", "").replace("\r", '')
            url_crawled.append(result)

    a = AmazonCrawler("Baby 0726.json", "Baby1222")
    #a.run_asin('https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/ref=zg_bs_unv_home-garden_1_510114_4')
    with open(r'G:\Dropbox\python\amazon_best_serller\json结果\Baby 0726.json', 'r+') as f:
        dt = json.load(f)
    for item in dt.keys():
        if dt[item]['is_bottom'] == 1:
            url = dt[item]['url']
            if url not in url_crawled:
                a.run_asin(url)
                with open(url_crawled_path,'a+', encoding='utf-8') as txt_file:
                    txt_file.write(url)
                    txt_file.write("\n")
    print('抓取完毕')

    #a.run_asin('https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/ref=zg_bs_unv_home-garden_1_510114_4')

    # rank = dt[item]['first_asin_rank']
    # name = dt[item]['name']
    # with open('G:\\bsr node.csv', 'a+') as csvfile:
    #     writer = csv.writer(csvfile)  

    #     writer.writerow([name, url, rank])
    # a.run_asin("https://www.amazon.com/Best-Sellers-Home-Kitchen-Bedroom-Sets/zgbs/home-garden/3732931/ref=zg_bs_nav_home-garden_3_1063308")
