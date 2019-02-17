import requests
from lxml import etree
import json

BASE_DIMAIN = "https://www.dytt8.net"  # 定义基础域名
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
}


# 获取电影列表页的链接
def movie_list_page():
    base_url = "https://www.dytt8.net/html/gndy/dyzz/list_23_{}.html"
    page_urls = []
    total_page = 189
    for x in range(1, total_page + 1):
        page_urls.append(base_url.format(x))

    return page_urls


# 传入电影列表页地址，返回这一页中每一部电影的详情页面链接
def get_detail_url(url):
    response = requests.get(url, headers=HEADERS)
    text = response.text
    html = etree.HTML(text)
    detail_urls = html.xpath("//table[@class='tbspan']//a[@href!='/html/gndy/dyzz/index.html']/@href")
    detail_urls = map(lambda x: BASE_DIMAIN + x, detail_urls)

    return detail_urls


# 通过电影的详情页面链接，获取电影的全部数据
def get_movie_content(url):
    movie = {}
    detail_response = requests.get(url, headers=HEADERS)
    detail_text = detail_response.content.decode(encoding="gb18030", errors="ignore")
    detail_html = etree.HTML(detail_text)

    if len(detail_html.xpath("//div[@id='Zoom']")) > 0:
        zoom = detail_html.xpath("//div[@id='Zoom']")[0]
    else:
        return movie            # 说明没有爬取成功，直接跳过返回一个空字典

    text_list = zoom.xpath(".//text()")       # 获取页面中的文本，进行过滤

    for (index, text) in enumerate(text_list):
        if text.startswith("◎译　　名"):
            movie["译　　名"] = text.replace("◎译　　名", "").strip()
        elif text.startswith("◎片　　名"):
            movie["片　　名"] = text.replace("◎片　　名", "").strip()
        elif text.startswith("◎年　　代"):
            movie["年　　代"] = text.replace("◎年　　代", "").strip()
        elif text.startswith("◎产　　地"):
            movie["产　　地"] = text.replace("◎产　　地", "").strip()
        elif text.startswith("◎国　　家"):
            movie["国　　家"] = text.replace("◎国　　家", "").strip()
        elif text.startswith("◎类　　别"):
            movie["类　　别"] = text.replace("◎类　　别", "").strip()
        elif text.startswith("◎语　　言"):
            movie["语　　言"] = text.replace("◎语　　言", "").strip()
        elif text.startswith("◎字    幕"):
            movie["字    幕"] = text.replace("◎字    幕", "").strip()
        elif text.startswith("◎上映日期"):
            movie["上映日期"] = text.replace("◎上映日期", "").strip()
        elif text.startswith("◎豆瓣评分"):
            movie["豆瓣评分"] = text.replace("◎豆瓣评分", "").strip()
        elif text.startswith("◎IMDb评分"):
            movie["IMDb评分"] = text.replace("◎IMDb评分", "").strip()
        elif text.startswith("◎片　　长"):
            movie["片　　长"] = text.replace("◎片　　长", "").strip()
        elif text.startswith("◎导　　演"):
            movie["导　　演"] = text.replace("◎导　　演", "").strip()
        elif text.startswith("◎编　　剧"):
            screenwriter = []
            screenwriter.append(text.replace("◎编　　剧", "").strip())
            for num in range(index + 1, index + 10):
                if (text_list[num].startswith("◎主　　演")):
                    break
                else:
                    screenwriter.append(text_list[num].strip())
            movie["编　　剧"] = screenwriter
        elif text.startswith("◎主　　演"):
            actors = []
            actors.append(text.replace("◎主　　演", "").strip())
            for num in range(index + 1, index + 10):
                if (text_list[num].startswith("◎简　　介")):
                    break
                else:
                    actors.append(text_list[num].strip())
            movie["主　　演"] = actors
        elif text.startswith("◎标　　签"):
            movie["标　　签"] = text.replace("◎标　　签", "").strip()
        elif text.startswith("◎简　　介"):
            conttent_index = index + 1
            movie["简　　介"] = text_list[conttent_index].strip()

    if len(zoom.xpath(".//td/a/@href")) > 0:
        download_url = zoom.xpath(".//td/a/@href")[0]
    elif len(zoom.xpath(".//td//a/@href")) > 0 :
        download_url = zoom.xpath(".//td//a/@href")[-1]
    else:
        download_url = "爬取失败，手动修改！"

    movie["下载地址"] = download_url
    
    return movie


if __name__ == '__main__':
    page_num = 1
    page_urls = movie_list_page()
    
    for (index, page_url) in enumerate(page_urls):
        file_name = "new_movie_" + str(index + page_num) + ".json"  # 设置存放每一页电影信息的json文件的名称
        one_page_movie_content = []  # 每一页中所有电影的信息
        movie_detail_urls = get_detail_url(page_url)
        
        idx = 1
        for movie_detail_url in movie_detail_urls:
            movie_content = get_movie_content(movie_detail_url)
            one_page_movie_content.append(idx)
            one_page_movie_content.append(movie_content)
            idx = idx + 1

        # 将爬取的每一页的电影数据，分别写入到一个json文件中
        one_page_movie_content_str = json.dumps(one_page_movie_content, ensure_ascii=False, indent=2)
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(one_page_movie_content_str)
        print("第" + str(index + page_num) + "页电影爬取完成，写入到" + file_name + "文件中")
