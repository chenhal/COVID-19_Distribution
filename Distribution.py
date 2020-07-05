# coding=utf-8
import urllib.request
from pyecharts.charts import Map
import requests
import re
import os
from pyecharts.globals import ThemeType
from pyecharts.charts import Bar, Grid, Line, Page, Pie
from pyecharts.faker import Faker
from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Pie, Timeline
url = "https://ncov.dxy.cn/ncovh5/view/pneumonia"
html = requests.get(url)
html.encoding = "utf-8"
#dq地区，qz确诊，zy治愈，sw死亡
dq = re.compile('window.getAreaStat = ([\s\S]*?)</script>').findall(html.text)
data1 = dq[0].replace('}catch(e){}', '')
data1 = eval(data1)
print(data1)
#dq地区，xcqz现存确诊，ljqz累计确诊，zy治愈，sw死亡
dq = []
xcqz = []
ljqz = []
zy = []
sw = []
for v in data1:
    dq.append(v['provinceShortName'])
    xcqz.append(v["currentConfirmedCount"])
    ljqz.append(v["confirmedCount"])
    zy.append(v['curedCount'])
    sw.append(v['deadCount'])
print(dq)
print(ljqz)
print(zy)
print(sw)
#print (dq,qz,sw,zy)
url1 = "https://voice.baidu.com/act/newpneumonia/newpneumonia/?from=osari_pc_1"
data = urllib.request.urlopen(url1).read().decode("utf-8", "ignore")
yf = re.compile('"trend":{"updateDate":(.*?)],').findall(data)
qzz = re.compile('"data":(.*?)}').findall(data)
#yuefeng月份quezhen总确诊yishi总疑似zhiyu总治愈shiwang总死亡xinzengquezhen新增确诊xinzengyisi新增疑似
yuefeng = re.compile('"(.*?)"').findall(yf[0] + "]")
quezhen = re.compile('[0-9]{1,7}').findall(qzz[0])
yishi = re.compile('[0-9]{1,7}').findall(qzz[1])
zhiyu = re.compile('[0-9]{1,7}').findall(qzz[2])
shiwang = re.compile('[0-9]{1,7}').findall(qzz[3])
xinzengquezhen = re.compile('[0-9]{1,7}').findall(qzz[4])
xinzengyisi = re.compile('[0-9]{1,7}').findall(qzz[5])


def map_visualmap() -> Map:
    c = (
        Map(init_opts=opts.InitOpts(theme=ThemeType.DARK)).add(
            "确诊人数", [list(z) for z in zip(dq, ljqz)],
            "china",
            is_map_symbol_show=False).
        set_global_opts(
            title_opts=opts.TitleOpts(title="全国疫情确诊人数分布图"),
            visualmap_opts=opts.VisualMapOpts(
                is_piecewise=True,
                pieces=[
                    {
                        "min": 10000,
                        "label": '大于10000',
                        "color": "#000000"
                    },
                    {
                        "min": 1000,
                        "max": 9999,
                        "label": '1000-9999人',
                        "color": "#840228"
                    },
                    {
                        "min": 100,
                        "max": 999,
                        "label": '100-499人',
                        "color": "#FF3030"
                    },
                    {
                        "min": 10,
                        "max": 99,
                        "label": '10-99人',
                        "color": "#FF7F50"
                    },
                    {
                        "min": 0,
                        "max": 9,
                        "label": '1-9人',
                        "color": "#FFDEAD"
                    },
                    # {"value": 0.004, "label": '123（自定义特殊颜色）', "color": 'grey'},# //表示 value 等于 123 的情况
                    # {"max": 0, "color": "blue"}     # 不指定 min，表示 min 为无限大（-Infinity）。
                ],
            ),
        ))
    return c


def bar_datazoom_slider() -> Bar:
    c = (Bar(init_opts=opts.InitOpts(
        theme=ThemeType.DARK)).add_xaxis(dq).add_yaxis("治愈人数", zy).add_yaxis(
            "死亡人数", sw).set_global_opts(
                title_opts=opts.TitleOpts(title="全国疫情治愈人数与死亡人数分布图"),
                datazoom_opts=[opts.DataZoomOpts()],
            ))
    return c


def overlap_line_scatter() -> Bar:
    x = yuefeng
    bar = (Bar(
        init_opts=opts.InitOpts(theme=ThemeType.DARK)).add_xaxis(x).add_yaxis(
            "治愈总人数", zhiyu).add_yaxis("死亡总人数", shiwang).set_global_opts(
                title_opts=opts.TitleOpts(title="全国疫情趋势图")))
    line = (Line(
        init_opts=opts.InitOpts(theme=ThemeType.DARK)).add_xaxis(x).add_yaxis(
            "确诊总人数", quezhen).add_yaxis("疑似总人数", yishi))
    bar.overlap(line)
    return bar


def line_base() -> Line:
    c = (Line(init_opts=opts.InitOpts(
        theme=ThemeType.DARK)).add_xaxis(yuefeng).add_yaxis(
            "新增确诊人数",
            xinzengquezhen).add_yaxis("新增疑似人数", xinzengyisi).set_global_opts(
                title_opts=opts.TitleOpts(title="全国疫情新增趋势图")))
    return c


page = Page(layout=Page.SimplePageLayout, page_title='全国疫情图')
page.add(map_visualmap(), bar_datazoom_slider(), overlap_line_scatter(),
         line_base())
page.render("全国疫情图.html")
os.system(r"全国疫情图.html")