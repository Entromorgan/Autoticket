# Autoticket
大麦网自动抢票工具

## Preliminary
Python 3.6+

## Set up
Firefox Browser (测试版本：v68.0.1.7137)

geckodriver.exe (测试版本：v0.24.0)

pip install selenium

## Basic usage
在config.json中输入相应配置信息，具体说明如下：
{
    "sess": [ # 场次优先级列表，如本例中共有三个场次，根据下表，则优先选择1，再选择2，最后选择3；也可以仅设置1个。
        1,
        2,
        3,
    ],
    "price": [ # 票价优先级，如本例中共有三档票价，根据下表，则优先选择1，再选择3；也可以仅设置1个。
        1,
        3
    ],
    "real_name": 2, # 实名者序号，如本例中共有两位实名者，根据序号，选择第二位实名者。
    "damai_url": "https://www.damai.cn/", # 大麦网官网网址
    "target_url": "https://detail.damai.cn/item.htm?id=599834886497" # 目标购票网址
}

![avatar](/picture/1.png)

![avatar](/picture/2.png)

若是首次登录，根据终端输出的提示，依次点击登录、扫码登录，代码将自动保存cookie文件（cookie.pkl）

使用前请将待抢票者的姓名、手机、地址设为默认。

## Advance usage
最后成功测试运行时间：2019-08-07。

此方法太过于依赖大麦网页面源码的元素的title、Xpath、class name，若相应的绝对路径寻找不到则代码无法运行。

建议自己先测试一遍，自行修改相应的绝对路径或用更好的定位方法替代。

本代码中用到的title如下：

1. '大麦网-全球演出赛事官方购票平台' # 大麦网官网标题

2. '大麦登录' # 大麦网登录页面标题

3. '支付' # 支付页面标题

本代码中用到的Xpath如下：

1. '/html/body/div[2]/div[2]/div/div[2]/div[2]/div[1]' # 实名者/观演人栏

2. '/html/body/div[2]/div[2]/div/div[9]/button' # 同意以上协议并提交订单按钮

本代码中用到的class name如下：

1. perform__order__select # 本类包括场次选项和票档选项

2. select_left # 选项的左侧项，包括场次和票档

3. select_right_list_item # 选项的右侧项，包括场次1，2，3...和票档1，2，3...

4. presell # 场次选项的左上角标，包括无票和预售

5. notticket # 票档选项的左上角标，若存在，则为缺货登记

6. buybtn # 目标购票页面中的抢购按钮，其text内容包含多种情况，如即将开抢、立即预订、立即购买、选座购买、提交缺货登记

## Ref
修改自以下两个Repo:

1. Oliver0047: https://github.com/Oliver0047/Concert_Ticket

2. MakiNaruto: https://github.com/MakiNaruto/Automatic_ticket_purchase
