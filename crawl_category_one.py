from crawl_category_all import AmazonCrawler
import re

if __name__=="__main__":
    #  第二个文件名为mt保存的文件
    a=AmazonCrawler(category_file_name="Pet Supplies 0803.json")
    url = "https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/ref=zg_bs_nav_0"
    name = re.findall('/(Best-Sellers-.*?)/',url)
    if not name:
        print ("此链接不符合bestSeller链接要求")
    else:
        a.run_category_url(url,name[0])
    print(f"正常结束了-{name}")
