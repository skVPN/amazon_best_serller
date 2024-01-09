# 公众号codegank开源分享

# 方案说明:
亚马逊BEST SELLER 类目爬虫：
1.获取任意BEST SELLER类目数
2.如果第一个的asin排名小于4000则继续 ，也不用去看子类目了，判断为最底层类目，结束递归

# 环境安装：windows
    - 使用插件：edge浏览器,使用插件：edge浏览器插件：SwitchyOmega
    - 中间人：mitmprox 
    - python3环境


- 下列三种模式，如果并发执行有触发反爬风险，建议单列执行

##  爬所有类目:
### 规则说明： 打开种子，判断不在种子页面中，且判断第一个asin的类目排名有没有小于4000，否则继续打开向下，保存到category.json,
- 默认配置： base.html 为https://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_beauty_0_1 内容
- 开启命令 python crawl_category_all.py   

# 爬指定单个类目，爬取商品100排名 ：
- 打开crawl_asin.py ，输入类目链接
- 开启命令 python crawl_asin.py 

# 爬指定单个类目下的所有子类目 ：
- 打开crawl_category_one.py ，输入：beseller_url 和存储category名称

## 调速说明：
  更改crawl_category_all.py中48行，每次打开浏览器后的随机休眠时间
              time.sleep(random.randint(10,25))
  使用代理示例: mitmdump  --mode upstream:http://127.0.0.1:7890/ -s  .\mt.py
  不使用代理示例：mitmdump --mode .\mt.py

逻辑说明：
1,下载文件到本地，如果已经存在了，则直接使用html,否则调用浏览器打开链接并被中间人下载
2,category.json 为输出结果
3,需二次开发联系微信公众号codegank
"""
