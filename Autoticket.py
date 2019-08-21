# coding: utf-8
from json import loads
from time import sleep, time
from pickle import dump, load
from os.path import exists
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Concert(object):
    def __init__(self, session, price, real_name, nick_name, ticket_num, damai_url, target_url):
        self.session = session # 场次序号优先级
        self.price = price # 票价序号优先级
        self.real_name = real_name # 实名者序号
        self.status = 0 # 状态标记
        self.time_start = 0 # 开始时间
        self.time_end = 0 # 结束时间
        self.num = 0 # 尝试次数
        self.type = 0 # 目标购票网址类别
        self.ticket_num = ticket_num # 购买票数
        self.nick_name = nick_name # 用户昵称
        self.damai_url = damai_url # 大麦网官网网址 
        self.target_url = target_url # 目标购票网址
        
        if self.target_url.find("detail.damai.cn") != -1:
            self.type = 1
        elif self.target_url.find("piao.damai.cn") != -1:
            self.type = 2
        else:
            self.type = 0
            raise Exception("***Error:Unsupported Target Url Format:{}***".format(self.target_url))
            self.driver.quit()
    
    
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
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台')!=-1: # 等待网页加载完成
            sleep(1)
        print("###请扫码登录###")
        while self.driver.title == '大麦登录': # 等待扫码完成
            sleep(1)
        dump(self.driver.get_cookies(), open("cookies.pkl", "wb")) 
        print("###Cookie保存成功###")
    
    
    def set_cookie(self):
        try:
            cookies = load(open("cookies.pkl", "rb")) # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain':'.damai.cn', # 必须有，不然就是假登录
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
        print('###开始登录###')
        if not exists('cookies.pkl'):# 如果不存在cookie.pkl,就获取一下
            self.get_cookie()
        self.driver.get(self.target_url)
        self.set_cookie()
     
    
    def enter_concert(self):
        print('###打开浏览器，进入大麦网###')
        self.driver = webdriver.Firefox() # 默认火狐浏览器
        self.driver.maximize_window()
        self.login()
        self.driver.refresh()
        try:
            if self.type == 1: # detail.damai.cn
                locator = (By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/a[2]/div")
            elif self.type == 2: # piao.damai.cn
                locator = (By.XPATH, "/html/body/div[1]/div/ul/li[2]/div/label/a[2]")
            element = WebDriverWait(self.driver, 3, 0.3).until(EC.text_to_be_present_in_element(locator,self.nick_name))
            self.status = 1
            print("###登录成功###")
        except:
            self.status=0
            raise Exception("***错误：登录失败,请删除cookie后重试***") 
            self.driver.quit()
    
    
    def choose_ticket_1(self): # for type 1, i.e., detail.damai.cn           
        self.time_start = time() 
        print("###开始进行日期及票价选择###")
        
        while self.driver.title.find('确认订单') == -1:  # 如果跳转到了确认界面就算这步成功了，否则继续执行此步
            '''###自动添加购票数###
            try:
                self.driver.find_elements_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div[7]/div[2]/div/div/a[2]')[0].click()   #购票数+1(若需要)
            except:
                print("购票数添加失败")
            '''
            self.num += 1
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
            # print('可选场次数量为：{}'.format(len(session_list)))
            for i in self.session: # 根据优先级选择一个可行场次
                j = session_list[i-1]
                k = self.isClassPresent(j, 'presell', True)
                if k: # 如果找到了带presell的类
                    if k.text == '无票':
                        continue
                    elif k.text == '预售':
                        j.click()
                        break
                else:
                    j.click()
                    break

            price_list = price.find_elements_by_class_name('select_right_list_item')
            # print('可选票档数量为：{}'.format(len(price_list)))
            for i in self.price:
                j = price_list[i-1]
                k = self.isClassPresent(j, 'notticket')
                if k: # 存在notticket代表存在缺货登记，跳过
                    continue
                else:
                    j.click()
                    break
            
            buybutton = self.driver.find_element_by_class_name('buybtn')
            buybutton_text = buybutton.text
            
            if buybutton_text == "即将开抢" or buybutton_text == "即将开售":
                self.status = 2
                self.driver.get(self.target_url)
                print('###抢票未开始，刷新等待开始###')
                continue

            elif buybutton_text == "立即预订":
                for i in range(self.ticket_num-1): # 设置增加票数
                    self.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div[8]/div[2]/div/div/a[2]').click()
                buybutton.click()
                self.status = 3
                    
            elif buybutton_text == "立即购买":
                for i in range(self.ticket_num-1): # 设置增加票数
                    self.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div[8]/div[2]/div/div/a[2]').click()
                buybutton.click()
                self.status = 4                    
        
            elif buybutton_text == "选座购买": # 选座购买暂时无法完成自动化
                buybutton.click()
                self.status = 5
                print("###请自行选择位置和票价###") # 此处或可改成input，等待用户选完后反馈，继续抢票流程
                break
                    
            elif buybutton_text == "提交缺货登记":
                print('###抢票失败，请手动提交缺货登记###')  
                break  
            
            
    def choose_ticket_2(self): # for type 2, i.e., piao.damai.cn
        self.time_start = time() 
        print("###开始进行日期及票价选择###")
        
        while self.driver.title.find('订单结算页') == -1:  # 如果跳转到了确认界面就算这步成功了，否则继续执行此步
            self.num += 1
            session = self.driver.find_element_by_id('performList')
            session_list = session.find_elements_by_tag_name('li')
            print('可选场次数量为：{}'.format(len(session_list)))
            for i in self.session: # 根据优先级选择一个可行场次,目前暂时没有找到有不可行日期的案例
                j = session_list[i-1].get_attribute('class')
                if j == 'itm': # 未选中
                    price_list[i-1].find_element_by_tag_name('a').click()
                    break
                elif j == 'itm itm-sel': # 已选中
                     break
                elif j == 'itm itm-oos': # 无法选中
                    continue 
            sleep(0.7)
            price = self.driver.find_element_by_id('priceList')
            price_list = price.find_elements_by_tag_name('li')
            # print('可选票档数量为：{}'.format(len(price_list)))
            for i in self.price:
                j = price_list[i-1].get_attribute('class')
                if j == 'itm': # 未选中
                    price_list[i-1].find_element_by_tag_name('a').click()
                    break
                elif j == 'itm itm-sel': # 已选中
                     break
                elif j == 'itm itm-oos': # 无法选中
                    continue 
                    
            # 需要先判断是否存在按钮，才能确定是否会出现添加票
            sleep(0.5)
            try:
                buybutton = self.driver.find_element_by_id('btnBuyNow') # 要改成立即预订按钮的id
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
                        print("###请自行选择位置和票价###") # 此处或可改成input，等待用户选完后反馈，继续抢票流程
                        break
                    except:
                        print('---无法自行选座，尝试刷新---')
                        self.status = 2
                        self.driver.refresh()
            if self.ticket_num > 1:# 自动添加购票数
                add = self.driver.find_element_by_class_name('btn-add')
                while add.is_displayed() != True: # 等待显示
                    continue
                for i in range(self.ticket_num-1):
                    add.click()
            buybutton.click()
            # 目前没有找到缺货没有按钮的情况
            
    
    def check_order_1(self):
        if self.status in [3,4,5]:
            print('###开始确认订单###')
            print('###选择购票人信息###')   
            try:
                tb = WebDriverWait(self.driver, 10, 0.3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div[2]/div[1]')))
                lb = tb.find_elements_by_tag_name('label')[self.real_name-1] # 选择第self.real_name个实名者
                lb.find_element_by_tag_name('input').click()
            except:
                raise Exception("***错误：实名信息选择框没有显示***")
            # print('###不选择订单优惠###')
            # print('###请在付款完成后下载大麦APP进入订单详情页申请开具###')
            sleep(0.5)
            self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[9]/button').click() # 同意以上协议并提交订单
            '''
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
                element = WebDriverWait(self.driver, 10, 0.3).until(EC.title_contains('支付宝'))
                self.status = 6
                print('###成功提交订单,请手动支付###')
                self.time_end = time()
            except:
                print('---提交订单失败,请查看问题---')
                
                
    def check_order_2(self):
        if self.status in [3,4,5]:
            print('###开始确认订单###')
            print('###选择购票人信息###')   
            try:
                tb = WebDriverWait(self.driver, 3, 0.3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div[2]/div/div/div/h2/a')))
                tb.click()
                sleep(0.3)
                lb_list = self.driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[12]/div/div[2]/div/div[2]/div/table/tbody')
                lb_list.find_elements_by_tag_name('input')[self.real_name-1].click() # 选择第self.real_name个实名者
            except Exception as e:
                print("###实名信息选择框没有显示###")
            # print('###不选择订单优惠###')
            # print('###请在付款完成后下载大麦APP进入订单详情页申请开具###')
            self.driver.find_element_by_id('orderConfirmSubmit').click() # 同意以上协议并提交订单
            element = WebDriverWait(self.driver, 10, 2).until(EC.title_contains('选择支付方式'))
            element.find_element_by_xpath('/html/body/div[5]/div/div/div/ul/li[2]/a').click() # 默认选择支付宝
            element.find_element_by_xpath('/html/body/div[5]/div/div/form/div[2]/ul/li[1]/label/input').click()
            element.find_element_by_id('submit2').click() # 确认无误，支付
            self.status = 6
            print('###成功提交订单,请手动支付###')
            self.time_end = time()
            # print('###提交订单失败,请查看问题###') # 这里异常处理还有点问题
                        
                    
    def finish(self):
        if self.status == 6: # 说明抢票成功
            print("###经过%d轮奋斗，共耗时%f秒，抢票成功！请确认订单信息###"%(self.num,round(self.time_end-self.time_start,3)))
        else:
            self.driver.quit()


if __name__ == '__main__':
    try:
        with open('./config.json', 'r', encoding='utf-8') as f:
            config = loads(f.read())
            # params: 场次优先级，票价优先级，实名者序号, 用户昵称， 购买票数， 官网网址， 目标网址
        con = Concert(config['sess'], config['price'], config['real_name'], config['nick_name'], config['ticket_num'], config['damai_url'], config['target_url'])
        con.enter_concert()
        if con.type == 1: # detail.damai.cn
            con.choose_ticket_1()
            con.check_order_1()
        elif con.type == 2: # piao.damai.cn
            con.choose_ticket_2()
            con.check_order_2()
        con.finish()
    except Exception as e:
        print(e)
