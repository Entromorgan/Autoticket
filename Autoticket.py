# coding: utf-8
from json import loads
from os.path import exists
from pickle import dump, load
from time import sleep, time
# import io # 用于py2.7时解注释

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import sys # 用于py2.7时解注释

# reload(sys) # 用于py2.7时解注释

# sys.setdefaultencoding('utf-8') # 用于py2.7时解注释


class Concert(object):
    def __init__(self, session, price, date, real_name, nick_name, ticket_num, damai_url, target_url, browser):
        self.session = session  # 场次序号优先级
        self.price = price  # 票价序号优先级
        self.date = date # 日期选择
        self.real_name = real_name  # 实名者序号
        self.status = 0  # 状态标记
        self.time_start = 0  # 开始时间
        self.time_end = 0  # 结束时间
        self.num = 0  # 尝试次数
        self.type = 0  # 目标购票网址类别
        self.ticket_num = ticket_num  # 购买票数
        self.nick_name = nick_name  # 用户昵称
        self.damai_url = damai_url  # 大麦网官网网址
        self.target_url = target_url  # 目标购票网址
        self.browser = browser # 0代表Chrome，1代表Firefox，默认为Chrome
        self.total_wait_time = 3 # 页面元素加载总等待时间
        self.refresh_wait_time = 0.3 # 页面元素等待刷新时间
        self.intersect_wait_time = 0.5 # 间隔等待时间，防止速度过快导致问题

        if self.target_url.find("detail.damai.cn") != -1:
            self.type = 1
        elif self.target_url.find("piao.damai.cn") != -1:
            self.type = 2
        else:
            self.type = 0
            self.driver.quit()
            raise Exception("***Error:Unsupported Target Url Format:{}***".format(self.target_url))

            
    def isClassPresent(self, item, name, ret=False):
        try:
            result = item.find_element_by_class_name(name)
            if ret:
                return result
            else:
                return True
        except:
            return False

        
    def get_cookie(self):
        self.driver.get(self.damai_url)
        print("###请点击登录###")
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:  # 等待网页加载完成
            sleep(1)
        print("###请扫码登录###")
        while self.driver.title == '大麦登录':  # 等待扫码完成
            sleep(1)
        dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print("###Cookie保存成功###")

        
    def set_cookie(self):
        try:
            cookies = load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print('###载入Cookie###')
        except Exception as e:
            print(e)

            
    def login(self):
        if not exists('cookies.pkl'):  # 如果不存在cookie.pkl,就获取一下
            if self.browser == 0: # 选择了Chrome浏览器
                self.driver = webdriver.Chrome()
            elif self.browser == 1: # 选择了Firefox浏览器
                self.driver = webdriver.Firefox()
            else:
                raise Exception("***错误：未知的浏览器类别***")
            self.get_cookie()
            self.driver.quit()
        print('###打开浏览器，进入大麦网###')
        if self.browser == 0: # 选择了Chrome浏览器，并成功加载cookie，设置不载入图片，提高刷新效率
            options = webdriver.ChromeOptions()
            prefs = {"profile.managed_default_content_settings.images":2}
            options.add_experimental_option("prefs",prefs)
            self.driver = webdriver.Chrome(options=options)
        elif self.browser == 1: # 选择了火狐浏览器
            options = webdriver.FirefoxProfile()
            options.set_preference('permissions.default.image', 2)  
            self.driver = webdriver.Firefox(options)
        else: 
            raise Exception("***错误：未知的浏览器类别***")
        self.driver.get(self.target_url)
        self.set_cookie()
        # self.driver.maximize_window()
        self.driver.refresh()
        
        
    def enter_concert(self):
        self.login()
        try:
            if self.type == 1:  # detail.damai.cn
                locator = (By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/a[2]/div")
            elif self.type == 2:  # piao.damai.cn
                locator = (By.XPATH, "/html/body/div[1]/div/ul/li[2]/div/label/a[2]")
            WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                EC.text_to_be_present_in_element(locator, self.nick_name))
            self.status = 1
            print("###登录成功###")
        except Exception as e:
            print(e)
            self.status = 0
            self.driver.quit()
            raise Exception("***错误：登录失败,请检查配置文件昵称或删除cookie.pkl后重试***")

            
    def choose_ticket_1(self):  # for type 1, i.e., detail.damai.cn
        self.time_start = time()
        print("###开始进行日期及票价选择###")

        while self.driver.title.find('确认订单') == -1:  # 如果跳转到了确认界面就算这步成功了，否则继续执行此步
            self.num += 1 # 记录抢票轮数
            
            if self.date != 0: # 如果需要选择日期
                calendar = WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "functional-calendar")))
                datelist = calendar.find_elements_by_css_selector("[class='wh_content_item']") # 找到能选择的日期
                datelist = datelist[7:] # 跳过前面7个表示周一~周日的元素
                datelist[self.date - 1].click() # 选择对应日期
            
            selects = self.driver.find_elements_by_class_name('perform__order__select')
            # print('可选区域数量为：{}'.format(len(selects)))
            for item in selects:
                if item.find_element_by_class_name('select_left').text == '场次':
                    session = item
                    # print('\t场次定位成功')
                elif item.find_element_by_class_name('select_left').text == '票档':
                    price = item
                    # print('\t票档定位成功')

            session_list = session.find_elements_by_class_name('select_right_list_item')
            print('可选场次数量为：{}'.format(len(session_list)))
            if len(self.session) == 1:
                j = session_list[self.session[0] - 1].click()
            else:
                for i in self.session:  # 根据优先级选择一个可行场次
                    j = session_list[i - 1]
                    k = self.isClassPresent(j, 'presell', True)
                    if k:  # 如果找到了带presell的类
                        if k.text == '无票':
                            continue
                        elif k.text == '预售':
                            j.click()
                            break
                    else:
                        j.click()
                        break

            price_list = price.find_elements_by_class_name('select_right_list_item')
            print('可选票档数量为：{}'.format(len(price_list)))
            if len(self.price) == 1:
                j = price_list[self.price[0] - 1].click()
            else:
                for i in self.price:
                    j = price_list[i - 1]
                    k = self.isClassPresent(j, 'notticket')
                    if k:  # 存在notticket代表存在缺货登记，跳过
                        continue
                    else:
                        j.click()
                        break

            buybutton = self.driver.find_element_by_class_name('buybtn')
            buybutton_text = buybutton.text
            # print(buybutton_text)
            
            def add_ticket(): # 设置增加票数
                try:
                    for i in range(self.ticket_num - 1):  
                        addbtn = WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@class='cafe-c-input-number']/a[2]")))
                        addbtn.click()
                except:
                    raise Exception("***错误：票数增加失败***")

            if buybutton_text == "即将开抢" or buybutton_text == "即将开售":
                self.status = 2
                self.driver.refresh()
                print('---尚未开售，刷新等待---')
                continue

            elif buybutton_text == "立即预订":
                add_ticket()
                buybutton.click()
                self.status = 3

            elif buybutton_text == "立即购买":
                add_ticket()
                buybutton.click()
                self.status = 4

            elif buybutton_text == "选座购买":  # 选座购买暂时无法完成自动化
                # buybutton.click()
                self.status = 5
                print("###请自行选择位置和票价###")
                break

            elif buybutton_text == "提交缺货登记":
                print('###抢票失败，请手动提交缺货登记###')
                break

                
    def choose_ticket_2(self):  # for type 2, i.e., piao.damai.cn
        self.time_start = time()
        print("###开始进行日期及票价选择###")

        while self.driver.title.find('订单结算页') == -1:  # 如果跳转到了确认界面就算这步成功了，否则继续执行此步
            self.num += 1 # 记录抢票轮数
            if self.date != 0: # 如果要选择日期
                datepicker = WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "month")))
                datelist = datepicker.find_elements_by_tag_name("span") # 找出所有日期
                # print(len(datelist))
                validlist = []
                for i in range(len(datelist)): # 筛选出所有可选择日期
                    j = datelist[i]
                    k = j.get_attribute('class')
                    if k == 'itm z-show itm-undefined z-sel' \
                    or k == 'itm z-show itm-undefined' \
                    or k == 'itm itm-end z-show itm-undefined':
                        validlist.append(j)
                # print(len(validlist))
                validlist[self.date - 1].click()
            
            session = WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                EC.presence_of_element_located(
                    (By.ID, "performList")))
            # session = self.driver.find_element_by_id('performList')
            session_list = session.find_elements_by_tag_name('li')
            print('可选场次数量为：{}'.format(len(session_list)))
            for i in self.session:  # 根据优先级选择一个可行场次,目前暂时没有找到有不可行日期的案例
                j = session_list[i - 1]
                k = j.get_attribute('class').strip()
                if k == 'itm' or k == 'itm j_more':  # 未选中
                    j.find_element_by_tag_name('a').click()
                    break
                elif k == 'itm itm-sel' or k == 'itm j_more itm-sel':  # 已选中
                    break
                elif k == 'itm itm-oos':  # 无法选中
                    continue
            
            sleep(self.intersect_wait_time)
            
            price = WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                EC.presence_of_element_located(
                    (By.ID, "priceList")))            
            # price = self.driver.find_element_by_id('priceList')
            price_list = price.find_elements_by_tag_name('li')
            print('可选票档数量为：{}'.format(len(price_list)))
            for i in self.price:
                j = price_list[i - 1]
                k = j.get_attribute('class').strip()
                if k == 'itm' or k == 'itm j_more':  # 未选中
                    j.find_element_by_tag_name('a').click()
                    break
                elif k == 'itm itm-sel' or k == 'itm j_more itm-sel':  # 已选中
                    break
                elif k == 'itm itm-oos':  # 无法选中
                    continue

            buybutton = None
            try:
                buybutton = self.driver.find_element_by_id('btnBuyNow')  # 要改成立即预订按钮的id
                self.status = 3
            except:
                try:
                    buybutton = self.driver.find_element_by_id('btnBuyNow')
                    self.status = 4
                except:
                    print('###无法立即购买，尝试自行选座###')
                    try:
                        buybutton = self.driver.find_element_by_id('btnXuanzuo')
                        self.status = 5
                        print("###请自行选择位置和票价###")
                        break
                    except:
                        print('---尚未开售，刷新等待---')
                        self.status = 2
                        self.driver.refresh()
                        
            # 需要先判断是否存在按钮，才能确定是否会出现添加票
            if self.ticket_num > 1 and self.status not in [2, 5]:  # 自动添加购票数
                # add = self.driver.find_element_by_class_name('btn btn-add')
                add = WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "btn-add")))
                for i in range(self.ticket_num - 1):
                    add.click()
            buybutton.click()
            # 目前没有找到缺货没有按钮的情况

            
    def check_order_1(self):
        if self.status in [3, 4]:
            print('###开始确认订单###')
            button_xpath = " //*[@id=\"confirmOrder_1\"]/div[%d]/button" # 同意以上协议并提交订单Xpath
            button_replace = 8 # 当实名者信息不空时为9，空时为8
            if self.real_name: # 实名者信息不为空
                button_replace = 9
                print('###选择购票人信息###')
                try:
                    list_xpath = "//*[@id=\"confirmOrder_1\"]/div[2]/div[2]/div[1]/div[%d]/label/span[1]/input"
                    for i in range(len(self.real_name)): # 选择第i个实名者
                        WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                            EC.presence_of_element_located((By.XPATH, list_xpath%(i+1)))).click()
                except Exception as e:
                    print(e)
                    raise Exception("***错误：实名信息框未显示，请检查网络或配置文件***")
            submitbtn = WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                    EC.presence_of_element_located(
                        (By.XPATH, button_xpath%button_replace))) # 同意以上协议并提交订单
            submitbtn.click()  
            '''# 以下的方法更通用，但是更慢
            try:
                buttons = self.driver.find_elements_by_tag_name('button') # 找出所有该页面的button
                for button in buttons:
                    if button.text == '同意以上协议并提交订单':
                        button.click()
                        break
            except Exception as e:
                raise Exception('***错误：没有找到提交订单按钮***')
           '''
            try:
                WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                    EC.title_contains('支付宝'))
                self.status = 6
                print('###成功提交订单,请手动支付###')
                self.time_end = time()
            except Exception as e:
                print('---提交订单失败,请查看问题---')
                print(e)

                
    def check_order_2(self):
        if self.status in [3, 4]:
            print('###开始确认订单###')
            if self.real_name: # 实名者信息不为空
                print('###选择购票人信息###')
                try:
                    tb = WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                        EC.presence_of_element_located(
                        (By.CLASS_NAME, 'from-1')))
                    tb.find_element_by_tag_name('a').click() # 点击选择购票人按钮
                    
                    sleep(self.intersect_wait_time)
                    # 此处好像定位不到实名者框，还没有解决
                    lb_list = WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                        EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[3]/div[3]/div[12]/div/div[2]/div/div[2]/div/table/tbody'))) # 定位弹窗
                    lb = lb_list.find_elements_by_tag_name('input')
                    for i in range(len(self.real_name)):
                        lb[self.real_name[i] - 1].find_element_by_tag_name('input').click()  # 选择第self.real_name个实名者
                except Exception as e:
                    print(e)
            input('halt')
            WebDriverWait(self.driver, self.total_wait_time, self.refresh_wait_time).until(
                        EC.presence_of_element_located(
                        (By.ID, 'orderConfirmSubmit'))).click() # 同意以上协议并提交订单
            # self.driver.find_element_by_id('orderConfirmSubmit').click() 
            element = WebDriverWait(self.driver, 10, self.refresh_wait_time).until(EC.title_contains('选择支付方式'))
            element.find_element_by_xpath('/html/body/div[5]/div/div/div/ul/li[2]/a').click()  # 默认选择支付宝
            element.find_element_by_xpath('/html/body/div[5]/div/div/form/div[2]/ul/li[1]/label/input').click()
            element.find_element_by_id('submit2').click()  # 确认无误，支付
            self.status = 6
            print('###成功提交订单,请手动支付###')
            self.time_end = time()
            # print('###提交订单失败,请查看问题###') # 这里异常处理还有点问题

    def finish(self):
        if self.status == 6:  # 说明抢票成功
            print("###经过%d轮奋斗，共耗时%f秒，抢票成功！请确认订单信息###" % (self.num, round(self.time_end - self.time_start, 3)))
        else:
            self.driver.quit()


if __name__ == '__main__':
    # import datetime
    # startTime = datetime.datetime(2019, 9, 25, 9, 17, 7)  #定时功能：2019-9-25 09:17:07秒开抢
    # print('抢票程序还未开始...')
    # while datetime.datetime.now() < startTime:
    #     sleep(1)
    # print('开始进入抢票 %s' % startTime)
    # print('正在执行...')
    try:
        # with io.open('./config.json', 'r', encoding='utf-8') as f: # 用于py2.7时解注释
        with open('./config.json', 'r', encoding='utf-8') as f: # 用于py2.7时注释此处
                    config = loads(f.read())
                # params: 场次优先级，票价优先级，日期， 实名者序号, 用户昵称， 购买票数， 官网网址， 目标网址， 浏览器
        con = Concert(config['sess'], config['price'], config['date'], config['real_name'], config['nick_name'], config['ticket_num'],
                      config['damai_url'], config['target_url'], config['browser'])
    except Exception as e:
        print(e)
        raise Exception("***错误：初始化失败，请检查配置文件***")
    con.enter_concert()
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
