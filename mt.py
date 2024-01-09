from mitmproxy import ctx
import os 
import re
import urllib.parse
from datetime import datetime
from builtins import FileNotFoundError
from mitmproxy import http, ctx
from curl_cffi import requests
#  mitmdump  --mode upstream:http://127.0.0.1:10809/ -s -q .\mt.py"  

class JA3:

    def request(self,flow: http.HTTPFlow) -> None:
        # 获取请求的 URL
        url = flow.request.url
        print ("url+++",url)
        # 获取请求方法
        method = flow.request.method

        # 获取请求头部
        headers = dict(flow.request.headers)

        # 获取请求的 Cookie
        cookies = dict(flow.request.cookies)
        if 'Best-Sellers' not in url:
            return
        # 数据准备
        data = None
        if method == 'POST':
            # 获取请求体数据
            data = flow.request.text

        # 发送请求
        print ("use+++,cffi ")
        response = requests.request(method, url, headers=headers, cookies=cookies, data=data,verify=False)

        # 将响应内容设置为 mitmproxy 的响应
        flow.response = http.Response.make(
            response.status_code,
            response.content,
            dict(response.headers)
        )

class BASE:
    def writefile(self, category,filename, content):
        MY_PATH = os.environ.get('MY_PATH')
        if not MY_PATH:
            MY_PATH = 'MIT_CRAWL'
        self.PATH = MY_PATH
        filename = filename.replace("/","$").replace(":","@")

        filename=os.path.join(os.getcwd(), self.PATH,filename)
        dir_path = os.path.join(os.getcwd(), self.PATH)
        if not  os.path.exists(dir_path):
            os.makedirs(dir_path,exist_ok=True)
        if "mp4" not in filename:
            filename+=".html" 
        print ("save ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++,MY_PATH",filename)
        try:
            with open( filename, "wb" ) as f:
                f.write( content )
        except FileNotFoundError as e:
            ctx.log.info( "+++++Writing File ok: {}".format( filename ) )

class AmazonGrabber(BASE):   
    # https://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_baby-products_0_17720255011_2    # ?_encoding=UTF8&pg=2
    videos=[]
    category=""

    # def load(self, loader):
    #     loader.add_option(
    #         name="my_path",
    #         typespec=str,
    #         default="False",
    #         help="Add a count header to responses",
    #     )
    def response(self, flow):
        url = flow.request.url   
        if "www.amazon.com" in url:
            # print ('++++++++++,url',url)
            _asin = re.findall('/dp/(.*?)/',url)
            asin = _asin[0] if _asin else ""   #详情

            _key = re.findall('&k=([\s\S]*)[$&]?',url)  # 搜索

            key  = _key[0] if _key else ""   
            _page = re.findall('pg=(\d+)',url)  
            if not _page:
                _page = re.findall('ref=sr_pg_(\d+)',url)  
            page  = _page[0] if _page else ""   

            # if not key:
            #     _best_name =   re.findall('/(Best-Sellers-.*?)/',url)  # best_seller
            #     key  = _best_name[0] if _best_name else ""   
            if not key:
                _key = re.findall('https://www.amazon.com/(Best-Sellers.*?)/',url)  # Best-Sellers 
                key  = _key[0] if _key else ""    
            if key:
                key+=page      
            name =  asin or key 
            if name:
                name = name[100:] if len(name)>100 else name
                self.writefile(datetime.now().strftime("%Y-%m-%d"),name, flow.response.content )   

class TbGrabber(BASE):   
    # https://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_baby-products_0_17720255011_2    # ?_encoding=UTF8&pg=2
    videos=[]
    category=""
    def response(self, flow):
        url = flow.request.url   
        if "mtop.taobao.idle.awesome.detail" in url:
            print(flow.response.content)
class BlockImages:
    def response(self, flow):
        # print (flow.response.headers.get("content-type", ""), flow.request.url)
        if "image" in flow.response.headers.get("content-type", ""):
            # 屏蔽图片流量
            flow.response.content = b""
            flow.response.headers["content-type"] = "text/plain"

        if "video" in flow.response.headers.get("content-type", ""):
            # 屏蔽视频流量
            flow.response.content = b""
            flow.response.headers["content-type"] = "text/plain"
addons = [
    # start(),
    # JA3(),
    # PddGrabber(),
    AmazonGrabber(),
    TbGrabber(),
    BlockImages()
]
