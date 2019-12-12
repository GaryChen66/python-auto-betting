from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import xlrd
from datetime import datetime
import time
import pytz
import math
import schedule
import random
import xlwt
#import openpyxl

info = {
    "user_name": "lukicama",
    "user_pass": "testingbot12345",
}

time_run = []

def set_time(bet_type):
    if bet_type == 0:
        for i in range(1, 24):
            for j in range(3, 60, 5):
                if i < 10:
                    str_hour = '0' + str(i)
                else:
                    str_hour = str(i)
                if j < 10:
                    str_min = '0' + str(j)
                else:
                    str_min = str(j)
                str_time = str_hour + ':' + str_min
                time_run.append(str_time)
    else:
        for i in range(7, 22):
            if i < 10:
                str_hour = '0' + str(i)
            else:
                str_hour = str(i)
            str_time = str_hour + ':' + '40'
            time_run.append(str_time)

class Bettingbot:

    def __init__(self, username, password, url, result_url):
        self.username = username
        self.password = password
        self.url = url
        self.result_url = result_url
        self.bet_type = 0
        self.money_onAccount = 0
        self.statusA = 1
        self.statusB = 1
        self.statusC = 0
        self.maxNum_A = 1
        self.maxNum_B = 1
        self.maxNum_C = 1
        self.percent = 1
        self.trigger = 1
        self.count = 0
        self.row = 0
        self.maxcount = 10
        self.betnumber = 0
        self.increament_value = 0
        self.index = 0
        self.delta = 0
        self.check_flag = 1
        self.outputmoney = 0

        self.decA = 0
        self.decB = 0
        self.lostMax = 0
        self.lostMin = 0
        self.initState = []
        self.winNum = []
        self.totaltimes = 0
        self.isthird = 0

        self.is_checked = 1
        self.iscurrentbetwinner = 1
        self.currenttimes = 0

        self.workbook = xlrd.open_workbook('./input1.xlsx')
        self.outworkbook = xlwt.Workbook()
        self.ws = self.outworkbook.add_sheet("result")
        self.init_excel()
        
        self.ka = []
        self.kb = []
        self.money_risk = []
        self.prevResult = {"kolo": "", "datetime": "", "status": "", "amount": ""}
        self.driver = webdriver.Chrome('./chromedriver.exe')
    #    self.driver = webdriver.Chrome('./chromedriver')
        
    def init_excel(self):
        first_col = self.ws.col(0)
        first_col.width = 256 * 20
        self.ws.write(0, 0, "DateTime")
        self.ws.write(0, 1, "Kolo")
        self.ws.write(0, 2, "Amount")
        self.ws.write(0, 3, "Status")
        self.ws.write(0, 5, "Status A")
        self.ws.write(0, 6, "Status B")
        self.ws.write(0, 7, "Status C")
        self.ws.write(0, 8, "Next stake")
        self.ws.write(0, 9, "Left money")
             
    def closedriver(self):
        self.driver.quit()

    def get_exceldata(self):
        sheet = self.workbook.sheet_by_name("input")
        self.bet_type = int(sheet.cell_value(1, 4))
        self.maxNum_A = int(sheet.cell_value(1, 5))
        self.maxNum_B = int(sheet.cell_value(1, 6))
        self.maxNum_C = int(sheet.cell_value(1, 7))
        self.increament_value = float(sheet.cell_value(1, 8))
        self.betnumber = int(sheet.cell_value(1, 9))
        self.maxcount = int(sheet.cell_value(1, 10))
        self.totaltimes = int(sheet.cell_value(1, 11))

        self.decA = int(sheet.cell_value(7, 4))
        self.decB = int(sheet.cell_value(7, 5))
        self.lostMax = int(sheet.cell_value(7, 7))
        self.lostMin = int(sheet.cell_value(7, 8))
        
        for i in range(10, 30):
            self.initState.append(int(sheet.cell_value(i, 5)))
        
        for i in range(4, 9):
            self.money_risk.append(float(sheet.cell_value(4, i)))

        if self.betnumber == 30:
            self.isthird = 1
        
        self.percent = self.money_risk[0]    
        print(self.bet_type, self.betnumber, self.maxNum_A, self.maxNum_B, self.maxNum_C, self.increament_value, self.maxcount, self.money_risk)
        print(self.decA, self.decB, self.lostMax, self.lostMin, self.initState)
    
    def check_elementexists(self):
        xpath = '//*[@id="moneyOpen"]'
        driver = self.driver
        try:
            driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return True
        return False

    # login function
    def login(self):
#        print("login start to run: " + datetime.now(pytz.timezone('Europe/Zagreb')).time().strftime("%H:%M"))
        driver = self.driver
        driver.get(self.url)
        time.sleep(10)
        driver.find_element_by_xpath('//*[@id="username"]').send_keys(self.username)
        driver.find_element_by_xpath('//*[@id="password2"]').send_keys(self.password)
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="loginBtn"]').click()  # click login button

        timeout = 20
        element_present = EC.element_to_be_clickable((By.XPATH, '//*[@id="moneyOpen"]'))
        WebDriverWait(driver, timeout).until(element_present)
        driver.find_element_by_xpath('//*[@id="moneyOpen"]').click()  # click show money on account button
        time.sleep(3)
    #    driver.find_element_by_xpath('/html/body/div[1]/a[2]').click()

    def relogin(self):
        print("!!!!relogin start to run: " + datetime.now(pytz.timezone('Europe/Zagreb')).time().strftime("%H:%M"))
        driver = self.driver
        driver.get(self.url)
        time.sleep(10)
        driver.find_element_by_xpath('//*[@id="username"]').send_keys(self.username)
        driver.find_element_by_xpath('//*[@id="password2"]').send_keys(self.password)
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="loginBtn"]').click()  # click login button
        time.sleep(2)
        driver.get(self.result_url)
        time.sleep(5)

    # select next number to bet
    def select_BetNumber(self):
        print("get_nextNumber is running")
        intialState = self.initState
#        self.nextStake = 2
        is_checked = 0
        betnumber = random.randint(1, 20)
        if self.iscurrentbetwinner == 1:
            
            for i in range(self.lostMax, self.lostMin - 1, -1):
                if is_checked == 1:
                    break
                for j in range(20):
                    if i == intialState[j]:
                        betnumber = j + 1
                        is_checked = 1
                        break
        print("  next bet number", betnumber)
        return betnumber
        
        
    # italy bet
    def bet_italy(self):
        print("bet_italy start to run: " + datetime.now(pytz.timezone('Europe/Zagreb')).time().strftime("%H:%M"))
        driver = self.driver
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="loto-countries"]/div[2]').click()  # click loto by country
        time.sleep(3)
        driver.find_element_by_partial_link_text('Win for life Classico').click()  # click italy loto
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="main-lottobetting-content"]/div[2]/div[1]/table/tbody/tr[2]').click()
        xpath = '//*[@id="main-lottobetting-content"]/div[2]/div[1]/table/tbody/tr[3]/td/ul/li['
        
        if self.betnumber == 30:
            betnumber = 2 * random.randint(1, 20)
        else:
            betnumber = self.betnumber * 2
        xpath = xpath + str(betnumber) + ']'
        time.sleep(5)
        element = driver.find_element_by_xpath(xpath)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="input"]').clear()
        driver.find_element_by_xpath('//*[@id="input"]').send_keys(self.nextStake)
        driver.find_element_by_xpath('//*[@id="submit-ticket"]').click()
        time.sleep(10)
        element = driver.find_element_by_link_text('UPLATI')  # payment button
        driver.execute_script("arguments[0].click();", element)
        
        element_present = EC.text_to_be_present_in_element((By.XPATH, '//*[@id="slip"]/h2'), 'LISTIĆ JE UPLAĆEN')
        WebDriverWait(driver, 10).until(element_present)
        
    # bet hungary
    def bet_hungary(self):
        print("bet_hungary start to run: " + datetime.now(pytz.timezone('Europe/Zagreb')).time().strftime("%H:%M"))
        driver = self.driver
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="loto-countries"]/div[2]').click()  # click loto by country
        time.sleep(3)
        driver.find_element_by_partial_link_text('Putto').click()  # choose hungary lotto
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="main-lottobetting-content"]/div[2]/div[1]/table/tbody/tr[2]').click()
        xpath = '//*[@id="main-lottobetting-content"]/div[2]/div[1]/table/tbody/tr[3]/td/ul/li['
        
        if self.betnumber == 0:
            betnumber = 2 * random.randint(1, 20)
        if self.betnumber == 20:
            betnumber = 2 * self.betnumber
        if self.betnumber == 30:
            betnumber = 2 * self.select_BetNumber()

        xpath = xpath + str(betnumber) + ']'
        time.sleep(5)
        element = driver.find_element_by_xpath(xpath)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="input"]').clear()
        driver.find_element_by_xpath('//*[@id="input"]').send_keys(self.nextStake)
        driver.find_element_by_xpath('//*[@id="submit-ticket"]').click()
        time.sleep(10)
        element = driver.find_element_by_link_text('UPLATI')  # payment button
        driver.execute_script("arguments[0].click();", element)
        
        element_present = EC.text_to_be_present_in_element((By.XPATH, '//*[@id="slip"]/h2'), 'LISTIĆ JE UPLAĆEN')
        WebDriverWait(driver, 10).until(element_present)
        
    # get amount of next stake
    def get_sum(self, k):
        sum = 0
        for kval in k:
            sum += float(kval)
        return sum
    
    # get amount of money on my account
    def get_accountmoney(self):
        print("get_accountmoney start to run: " + datetime.now(pytz.timezone('Europe/Zagreb')).time().strftime("%H:%M"))
        driver = self.driver
        driver.get(self.url)
        time.sleep(5)
        money_str = driver.find_element_by_xpath('//*[@id="userBalance"]').text
        money_str1 = money_str.split(",")[0]
        money_str2 = money_str1.replace(".", "")
        self.outputmoney = int(money_str2)
        if self.check_flag == 1:
            self.money_onAccount = int(money_str2)
            self.check_flag = 0
        print("  money on Account, check_flag:", self.money_onAccount, self.check_flag)
    
    # get amount of next stake
    def get_nextstake(self, statusA, statusB):
        print("get_nextstake start to run: " + datetime.now(pytz.timezone('Europe/Zagreb')).time().strftime("%H:%M"))
        total_kb = self.get_sum(self.kb)
        base = (1 / total_kb) * self.money_onAccount * self.kb[statusB-1]
        total_ka = self.get_sum(self.ka)
        print(total_ka, total_kb, base)
        
        temp = round((1 / total_ka * base * float(self.ka[statusA-1]) * self.percent), 2) + self.delta
        temp = round(temp, 2)
    
        if temp < 2:
            temp += 1
        temp = round(temp, 2)
        self.nextStake = str(temp).replace(".", ",")
        print("  NextStake, Percent, delta: ", self.nextStake, self.percent, self.delta)

    #scrape win numbers
    def scrapeWinNumbers(self):
        self.winNum = []
        driver = self.driver
#        driver.get(self.result_url)
        driver.find_element_by_xpath('//*[@id="detailsBtn1"]').click()
        time.sleep(5)
   
        for i in range(1, 9):
            xpath = '//*[@id="kladionica-history"]/div[4]/ul[2]/li['
            xpath = xpath + str(i) + ']'
            temp = driver.find_element_by_xpath(xpath).text
            self.winNum.append(int(temp))
        print("win numbers:", self.winNum)
    
    def updateInitState(self):
        print("update inital running")
        for i in range(1, 21):
            if self.winNum.count(i) > 0:
                self.initState[i - 1] = 0
            else:
                self.initState[i - 1] += 1
        print(" updated value", self.initState)

    # get previous result
    def get_result(self):
        self.is_checked = 0
        print("get result function start to run: " + datetime.now(pytz.timezone('Europe/Zagreb')).time().strftime("%H:%M"))
        driver = self.driver
        driver.get(self.result_url)
        time.sleep(5)
        self.prevResult["kolo"] = driver.find_element_by_xpath('//*[@id="summary"]/tbody/tr[1]/td[3]').text
        self.prevResult["datetime"] = driver.find_element_by_xpath('//*[@id="summary"]/tbody/tr[1]/td[5]').text
        self.prevResult["amount"] = driver.find_element_by_xpath('//*[@id="summary"]/tbody/tr[1]/td[7]').text
        condition = driver.find_element_by_xpath('//*[@id="summary"]/tbody/tr[1]/td[9]').text
#        condition = 'Nedobitni'
        while True:
            if condition == 'Nedobitni' or condition == 'Dobitni':
                break
            else:
                time.sleep(20)
                driver.get(self.result_url)
                time.sleep(10)
                try:
                    condition = driver.find_element_by_xpath('//*[@id="summary"]/tbody/tr[1]/td[9]').text
                except Exception:
                    print("Nosuchelement exception occured")
                    self.relogin()
                    condition = driver.find_element_by_xpath('//*[@id="summary"]/tbody/tr[1]/td[9]').text
                    continue
        if condition == 'Dobitni':
            self.iscurrentbetwinner = 1
        else:
            self.iscurrentbetwinner = 0

        self.prevResult["status"] = condition

        if self.isthird == 1:
            self.scrapeWinNumbers()
        
        self.row += 1
        print("  previous result, row: ", self.prevResult, self.row)
        self.is_checked = 1
        self.currenttimes += 1
        driver.get(self.url)

    # get counter A, B, C status
    def get_status(self):
        print("get_status start to run: " + datetime.now(pytz.timezone('Europe/Zagreb')).time().strftime("%H:%M"))
        self.statusC += 1
        
        if self.prevResult["status"] == 'Nedobitni':
            self.statusA += 1
        else:
            self.delta = self.increament_value * self.statusA
            if self.decA == 0:
                self.statusA = 1
            else:
                self.statusA -= self.decA
                if self.statusA < 1:
                    self.statusA = 1
        
        if self.statusA > self.maxNum_A:
            self.statusB += 1
            self.statusA = 1
            self.statusC = 0
            self.delta = 0

        if self.statusB > self.maxNum_B:
            self.index += 1
            if self.index < 5:
                if self.money_risk[self.index] != 0:
                    self.statusA = 1
                    self.statusB = 1
                    self.statusC = 0
                    self.count = 0
                    self.delta = 1
                    self.check_flag = 1
                    self.percent = self.money_risk[self.index]
                else:
                    self.trigger = 0
            else:
                self.trigger = 0        

        if self.statusC > self.maxNum_C:
            self.statusA = 1
            if self.decB == 0:
                self.statusB = 1
            else:
                self.statusB -= self.decB
                if self.statusB < 1:
                    self.statusB = 1

            self.statusC = 0
            self.delta = 0
            self.check_flag = 1
            self.count += 1

        print("  A B C status, risk index, delta: ", self.statusA, self.statusB, self.statusC, self.index, self.delta)
        print(" count: ", self.count)
    
    # is stop now?
    def is_stop(self):
        if self.count >= self.maxcount or self.currenttimes >= self.totaltimes or self.statusB == 2:
            self.trigger = 0
        
    def set_ka(self):
        sheet = self.workbook.sheet_by_name("input")
        for row in range(self.maxNum_A):
            val = sheet.cell_value(row+1, 1)
            self.ka.append(val)
        print(self.ka)

    def set_kb(self):
        sheet = self.workbook.sheet_by_name("input")
        for row in range(self.maxNum_B):
            val = sheet.cell_value(row+1, 2)
            self.kb.append(val)
        print(self.kb)
        
    def save_result(self):
        self.ws.write(self.row, 0, self.prevResult["datetime"])
        self.ws.write(self.row, 1, self.prevResult["kolo"])
        self.ws.write(self.row, 2, self.prevResult["amount"])
        self.ws.write(self.row, 3, self.prevResult["status"])
        self.ws.write(self.row, 5, self.statusA)
        self.ws.write(self.row, 6, self.statusB)
        self.ws.write(self.row, 7, self.statusC)
        self.ws.write(self.row, 8, self.nextStake)
        self.ws.write(self.row, 9, self.outputmoney)
             
def betting_job(bot):
    print("-",bot.row,"Job start to run: " + datetime.now(pytz.timezone('Europe/Zagreb')).time().strftime("%H:%M"))
    bot.driver.get(bot.url)
    if(bot.check_elementexists()):
        bot.login()
    bot.get_accountmoney()
    bot.get_nextstake(bot.statusA, bot.statusB)
    if bot.is_checked == 1:
        if bot.bet_type == 0:
            bot.bet_hungary()
        else:
            bot.bet_italy()
    
    bot.get_result()
    bot.updateInitState()
    bot.save_result()
    bot.get_status()
    bot.is_stop()

#running the main funtion
if __name__ == "__main__":

    #initialize settings
    username = "lukicama"
    password = "testingbot12345"
    site_url = "https://www.lutrija.hr/lotokladenjestaro"
    result_url = "https://www.lutrija.hr/igraj/user/gamesHistory.html"
    
    #Set memory for betting bot class
    bot = Bettingbot(username, password, site_url, result_url)
    bot.get_exceldata()
    
    #Set time
    set_time(bot.bet_type)
    bot.set_ka()
    bot.set_kb()
    bot.login()
    """
    bot.scrapeWinNumbers()
    
    bot.get_accountmoney()
    bot.get_nextstake(bot.statusA, bot.statusB)
    """

    #time loop
    for at_time in time_run:
        schedule.every().day.at(at_time).do(betting_job, bot)

    #loop continuously
    while bot.trigger == 1 :
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception:
            print("Warning: exception occured")
            continue

    #End application
    print("End")
    bot.closedriver()
    filename = datetime.now().strftime("%Y-%m-%d %H_%M") + '.xls'
    bot.outworkbook.save(filename)