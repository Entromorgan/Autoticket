# Autoticket
大麦网自动抢票工具

时间与精力缘故，本仓库不再提供后续维护，其中内容仅供学习交流使用。

## Preliminary
Python 3.6 + pip 

Option1：Firefox（测试版本：v68.0.1.7137） + geckodriver（测试版本：v0.24.0）

Option2：Chrome （测试版本：v77.0.3865.90） + Chrome driver （测试版本：v77.0.3865.10）

注：[Release](https://github.com/Entromorgan/Autoticket/releases)中有测试版本的Windows driver，下载后请与.py文件放在同一文件夹下；代码本身支持Windows、Linux、MacOS，请移步[Wiki](https://github.com/Entromorgan/Autoticket/wiki/%E6%B5%8F%E8%A7%88%E5%99%A8%E9%A9%B1%E5%8A%A8)更换浏览器驱动

Mac上通过homebrew安装drivers:
1. `brew cask install chromedriver`
2. `brew install geckodriver`

## Step
【重要，用前必看！！！】

第一步：搭建python3+pip环境，可使用anaconda、pycharm等集成环境，或纯python环境 （Windows下的环境搭建流程可参考 [Windows搭建python3开发环境&卸载](https://www.jianshu.com/p/2f1acc6ff2c6))

第二步：依赖安装，`pip install -r requirements.txt`

第三步：复制`config.example.json`文件并将新其命名为`config.json`。按Basic usage中的说明填写`config.json`配置文件，其中real_name项的填写务必提前到目标购票网址“购票须知”处确认是否需要实名者，以及是一证一票还是一人多票，若无需实名购票，则real_name留空；若一证一票，则real_name的数量必须与ticket_num的数字相同；若一人多票，则real_name仅留一个，ticket_num可多张

注：config.json文件中的配置信息均为必填项，有些可以留空，但请勿删除，若未按说明填写正确，极有可能导致抢票失败

## Basic usage
在config.json中输入相应配置信息，具体说明如下：

{
    
    "sess": [ # 场次优先级列表，如本例中共有三个场次，根据下表，则优先选择1，再选择2，最后选择3；也可以仅设置1个
        1,
        2,
        3,
    ],
    "price": [ # 票价优先级，如本例中共有三档票价，根据下表，则优先选择1，再选择3；也可以仅设置1个
        1,
        3
    ],
    "date": 0, # 选择第几个日期，默认为0表示不选择
    "real_name": [# 实名者序号，如本例中共有两位实名者，根据序号，同时选择1，2位实名者，留空表示无需实名购票
        1,
        2
    ],
    "nick_name": "your_nick_name", # 用户的昵称，用于验证登录是否成功
    "ticket_num": 2, # 购买票数
    "damai_url": "https://www.damai.cn/", # 大麦网官网网址
    "target_url": "https://detail.damai.cn/item.htm?id=599834886497", # 目标购票网址
    "browser": 0 # 浏览器类别，0为Chrome（默认），1为Firefox
}

![avatar](/picture/1.png)

![avatar](/picture/2.png)

配置实名者时请查看购票须知中是否有相关要求，下面两张图分别表示没有、有实名需求的情况：

![avatar](/picture/3.png)

![avatar](/picture/4.png)

若是首次登录，根据终端输出的提示，依次点击登录、扫码登录，代码将自动保存cookie文件（cookie.pkl）。

使用前请将待抢票者的姓名、手机、地址设为默认，如存在多名实名者，请提前保存相关信息。

配置完成后执行python Autoticket.py即可，由于有启动延迟，建议提前一段时间打开程序。

## Advance usage
最后成功测试运行时间：2019-10-06。

此方法太过于依赖大麦网页面源码的元素的title、Xpath、class name、tag name等，若相应的绝对路径寻找不到则代码无法运行。

建议自己先测试一遍，自行修改相应的绝对路径或用更好的定位方法替代。

具体定位方案请参见[Wiki](https://github.com/Entromorgan/Autoticket/wiki/%E5%AE%9A%E4%BD%8D%E6%96%B9%E5%BC%8F)。

本代码可修改为防弹窗类异常的持续抢票，仅需修改代码末尾：解注释"while True"与"break"，注释"if True"即可。

    # while True: # 可用于无限抢票，防止弹窗类异常使抢票终止
    if True:
        try:
            if con.type == 1:  # detail.damai.cn
                con.choose_ticket_1()
                con.check_order_1()
            elif con.type == 2:  # piao.damai.cn
                con.choose_ticket_2()
                con.check_order_2()
            # break
        except Exception as e:
            print(e)
            con.driver.get(con.target_url)
    con.finish()

## Potential Problems
若遇到`selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version xx`这样的错误，说明当前Chrome的版本不够，需要升级成xx版本

## Change log
v0.1: 

基本功能实现：

  1）用户登录cookie记录
  
  2）场次、票档自动勾选，优先级设定，自动跳过无票/缺货登记
  
  3）实名者/观演人设定
  
v0.2：

鲁棒性提升：

  1）添加用户昵称，验证登录成功
  
  2）修改提交订单按钮的索引方式，增强适配性
  
v0.3:

增强适配性，添加piao.damai.cn类别网页支持

v0.4:

鲁棒性提升，修改终端输出内容，添加指定购买票数功能（暂未支持勾选多实名者）

v0.5:

改默认浏览器为Chrome，默认取消图片加载，修复了部分bug，支持detail类别网站的票数增减、多实名者勾选，调整部分定位方式，修改错误输出

v0.6:

增加日期选择功能，完善实名售票，增强异常处理与第2类网址适配
  
## To-do List

1. 鲁棒性增强（刷新稳定性）

2. 代码重构，拆分两类网址和两种浏览器，维持代码整洁

3. 速度提升（多用户多线程，减少页面元素加载）

4. 完善第2类网址（piao.damai.cn）实名购票功能

5. 适配手机APP端（可考虑使用Autojs）

## Ref
本代码修改自Ref 1，2两个Repo，参考了Ref 3。

1. Oliver0047: https://github.com/Oliver0047/Concert_Ticket

2. MakiNaruto: https://github.com/MakiNaruto/Automatic_ticket_purchase

3. JnuMxin: https://github.com/JnuMxin/damaiAuto
