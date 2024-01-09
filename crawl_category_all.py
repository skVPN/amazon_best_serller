from loguru import logger
import os
import time
import random
import re
import hashlib
import json
import html
import subprocess
import requests


class BaseCrawler():
    BROWSER = "msedge.exe"
    def restart_mit(self):
        # return 
        os.system("taskkill /IM mitmdump.exe /F")        
        time.sleep(5)
        start_mt_cmd = f"mitmdump -q -s mt.py"
        logger.info(f"start mit ...{start_mt_cmd}")

        subprocess.Popen(['start', 'cmd', '/c', start_mt_cmd], shell=True, creationflags=subprocess.DETACHED_PROCESS)
        time.sleep(5)

        # input("go on ?")
    def open_url(self, url):
        print(url)
        # cmd = f"""start {self.BROWSER} /new-tab  "{url}" --proxy-server='http://localhost:8080'"""
        cmd = f"""start {self.BROWSER}  "{url}" """

        os.system(cmd)
        print(cmd)
        # input('go on?')

    def open_url_andorid(self, url):  # use andorid
        print(url)
        # adb shell dumpsys window | findstr mCurrentFocu
        cmd = f"""adb shell am start -n com.android.chrome/com.google.android.apps.chrome.Main -d  {url}"""
        os.system(cmd)
        print(cmd)

    def open_url_execjs(self, url):  # use andorid
        print(url)
        target_url = f'http://192.168.2.131:5612/business/invoke?group=webClient&action=open&url={url}'
        requests.get(target_url)

    def read_file_list(self, path):
        file_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                f = os.path.join(root, file)
                file_list.append(f)
        return file_list
    
    def get_html(self,url,name):
        # return self.get_html_sekiro(url)
        return self.get_html_local(url,name)

    def get_html_sekiro(self,url):
        print(url)
        target_url = f'http://192.168.2.131:5612/business/invoke?group=webClient&action=open&url={url}'
        html = requests.get(target_url)
        return html.json().get("html")

    def get_html_local(self, url, name=None):
        for i in range(4):   # 重启mitmproxy
            for i in range(5):  # 重试5打开浏览器
                ret = self.get_stored(name)
                if ret:
                    return ret

                self.open_url_execjs(url)
                time.sleep(random.randint(13, 25))
                for i in range(6):   # 重试获取页面
                    file_list = self.read_file_list(self.PATH)
                    print ("find :path",self.PATH,name)

                    for f in file_list:
                        if self.is_hit_file(name,f):
                            with open(f, 'r', encoding="utf8") as fr:
                                html = fr.read()
                                logger.info(f"获取到html:{f},-name:{name}-isban:{'Request was throttled' not in html}")
                                if "Request was throttled" not in html:   #  请过过程中的特别情况
                                    # self.close_browser()
                                    return html
                    time.sleep(2)
            logger.info(f"下载没有获取到html:{name}")
            self.restart_mit()


    def is_hit_file(self,name,file_path):
        # 判断是否命中目标文件
        name = name.replace(".html","")
        if "Best-Sellers" in file_path:
            _name = re.findall('(Best-Sellers-?.*?)\.html', file_path)
            if _name and _name[0] == name:
                # logger.info(f"++获取到html:{file_path},-name:{name}")
                return True
        else:
            if name in file_path:
                # logger.info(f"++获取到html:{file_path},-name:{name}")
                return True


    def get_stored(self, name):

        for f in self.read_file_list(self.PATH):
                if self.is_hit_file(name,f):
                    with open(f, 'r', encoding="utf8") as fr:
                        html = fr.read()
                        if "Request was throttled"  in html:  # 发现特别情况,直接重新打开浏览器
                            return
                        return html
        logger.info(f"本地没有获取到html:{name},准备打开浏览器获取")

    def close_browser(self):
        # return
        os.system(
            f"taskkill /f /im  {self.BROWSER} 2>nul && echo msedge process killed. || echo msedge process not running.")


class AmazonCrawler(BaseCrawler):
    catgorys_key = []
    catgorys = {}
    MAX_RANK = 8000
    HOST = "https://www.amazon.com/"
    rank_json="asin_rank.json"

    def __init__(self, category_file_name="category.json",mt_file_name="MIT_CRAWL"):
        os.environ['MY_PATH'] = mt_file_name
        self.category_file_name = category_file_name
        self.category_save = {}
        self.rank_data={}
        self.PATH = mt_file_name
        self.restart_mit()

    def _pase(self, url, html, k, father_node=None):
        logger.info(f"_parse {url}, k:{k}")
        url = url.split("?")[0]
        category_data = self.parse_category(url, html, k, father_node)
        if category_data:
            children_node = category_data.get('children_node')
            first_asin_rank = category_data.get('first_asin_rank')
            if first_asin_rank > 0 and first_asin_rank < self.MAX_RANK:  # 如果第一个的asin排名小于4000则继续  -1也不用去看子类目了
                for _category in children_node:
                    url = self.HOST + _category['url']
                    url = url.split("?")[0]
                    k = _category["k"]
                    logger.info(f"第{k}级类目,name:{_category['name']},father_node:{category_data.get('father_node')}{url}")
                    if _category['name'] not in self.catgorys_key:  # for 去重正在爬取：第20名的asin的排名
                        self.catgorys_key.append(_category['name'])
                        name = re.findall('/(Best-Sellers-?.*?)/', url)[0] + ".html"
                        html = self.get_html(url, name)
                        self._pase(url, html, k, _category['father_node'])
                try:
                    self.close_browser()
                    # os.system("adb shell pm clear --cache com.android.chrome")

                    pass
                except Exception as e:
                    pass

    def run_category_url(self, start_url=None, name=None):
        # 从base.html中获取初始类目种子，
        # 打开种子，判断不在种子页面中，且判断第一个asin的类目排名有没有小于4000，否则继续打开向下，保存到category.json,
        # 打开best_seller页面，拼接第二页，保存到best_seller.json
        if not start_url:
            start_url = "https://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_beauty_0_1"
        k = 1
        if not name:
            name = re.findall('/(Best-Sellers-?.*?)/', start_url)[0]
        # self.open_url("https://www.amazon.com")

        html = self.get_html(start_url, name)
        self._pase(start_url, html, k)
        with open(self.rank_json, 'w') as fw:
            fw.write(json.dumps(self.rank_data))
        with open(self.category_file_name, 'w+') as fw:
            fw.write(json.dumps(self.category_save))
        print(f"正常结束了-{name}")

    def parse_category(self, url, html, k=1, father_node=None):
        # {"k",1"name":"xxxx","url":"","children_node":[{"name"}]}
        if not html or 'p13n-zg-nav-tree-all_style_zg-selected' not in html:
            return
        node = re.findall('_p13n-zg-nav-tree-all_style_zg-selected__1SfhQ">(.*?)<', html)[0]
        _re = f'">{node}.*?role="group"(.*?)<script>'
        # print(_re)
        is_children_node = re.findall(_re, html)
        node = node.replace(", ", " ").replace("&amp;", "&")
        data = {"k": k, "name": node, "url": url, "children_node": [], "father_node": father_node}

        if is_children_node:
            _category = re.findall('treeitem.*?/(Best-Sellers-?.*?)">(.*?)<', is_children_node[0])
            if _category:
                for i in _category:
                    data["children_node"].append({"k": k + 1, "name": i[1], "url": i[0], "father_node": node})

        key = hashlib.md5(f"{node}{k}".encode(encoding='utf-8')).hexdigest()
        # if key not in category_save:
        rank = -1
        asin = ""
        if "music/player" not in url:
            asin, rank = self.get_first_asin_rank(html)
        data['first_asin_rank'] = rank
        data['first_asin'] = asin
        data['is_bottom'] = 0
        if not data.get("children_node") and rank < 4000:
            data['is_bottom'] = 1
        self.category_save.update({key: data})
        logger.info(f"+++存储类目:{self.category_file_name},{node}{k},{key}:{data}")
        return data

    def get_first_asin_rank(self, html):
        _asin = re.findall('zg-bdg-text">#1<.*?href="(.*?)"', html)
        if "Sorry, there are no Best Sellers available in this category" in html or not _asin:
            return None, 999999
        link = _asin[0]
        url = self.HOST + link
        _asin = re.findall('/dp/(\w{10})', url)
        if not _asin:
            return "", 999999
        asin = _asin[0]
        logger.info(f"第一名的asin的url:{url},asin:{asin}")
        rank_data = self.get_rank()
        rank = rank_data.get(asin)
        if not rank:
            html = self.get_html(url, asin)
            rank = -1
            _rank =  re.findall('Best Sellers Rank.*?#(\d+.*?)\s', html)
            if _rank:
                rank =  int(_rank[0].replace(",","").replace(" ",""))
        self.rank_data.update({asin: rank})

        logger.info(f"第一名的asin的排名:{asin},{rank}")
        return asin, rank

    def get_rank(self):
        if not self.rank_data:
            self.rank_data = {}
            # with open(self.rank_json, 'r') as f:
            #     self.rank_data = json.load(f) or {}

        return self.rank_data

    def run_asin(self, category_url):
        name = re.findall('/(Best-Sellers-?.*?)/', category_url)[0]
        html_1 = html.unescape(self.get_html(category_url, name))

        page = 2
        category_url2 = category_url.split("?")[0] + "?_encoding=UTF8&pg=%s" % page
        html_2 = html.unescape(self.get_html(category_url2, name + "%s" % page))

        rank_asin_dict = {}
        for html_str in [html_1, html_2]:
            _asins = re.findall('"id":"(\w{10})".*?"render.zg.rank":"(\d+)"', html_str)
            if _asins:
                for _asin in _asins:
                    rank_asin_dict[_asin[1]] = _asin[0]

        # print(rank_asin_dict)
        # os.system("taskkill /f /im msedge.exe")

        for rank, asin in rank_asin_dict.items():
            url = f"https://www.amazon.com//dp/{asin}//?psc=1"
            logger.info(f"正在爬取：第{rank}名的asin的排名:{asin},{url}")
            if self.get_html(url, asin):
                logger.info(f"爬取成功：第{rank}名的asin的排名:{asin},{url}")
            #############以下本人添加
                try:
                    asin_html = self.get_html(url,asin)
                    _asin_rank = re.findall('Best Sellers Rank.*?#(\d+.*?)\s', asin_html)
                    if _asin_rank:
                        asin_rank= int(_asin_rank[0].replace(",", "").replace(" ", ""))
                except:
                    asin_rank = 9999999
                try:
                    if asin_rank > self.MAX_RANK:
                        logger.info(f"{asin}：的排名:{asin_rank},大于预定的最大目标排名{self.MAX_RANK},不再继续往下爬去")
                        return
                    else:
                        logger.info(f"{asin}：的排名:{asin_rank},小于预定的最大目标排名{self.MAX_RANK},继续往下爬去")
                except:
                    logger.info(f"{asin}：的排名爬取出现未知错误")
                    continue
            ##################################################################
        # os.system("taskkill /f /im msedge.exe")


if __name__ == "__main__":
    a=AmazonCrawler()
    a.run_category_url()  # 爬取所有类目