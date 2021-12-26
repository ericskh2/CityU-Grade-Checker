import os
from selenium import webdriver
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import sys
from datetime import datetime

class GradeChecker:

    # Edit all configurations including login id and password here
    def configuration(self):
        self.EID = 'myeid'
        self.PASSWORD = 'mypassword'
        self.TELEGRAM_BOT_TOKEN = 'mybottoken'
        self.TELEGRAM_BOT_VERIFICATIONCODE = 'secret'
        self.CITYU_AIMS_URL = 'http://www.cityu.edu.hk/cityu/qlink/aims.htm'
        self.CRAWL_INTERVAL = 30

    def setup_selenium(self):
        # chrome_bin_path = os.environment.get('GOOGLE_CHROME_BIN')
        # chrome_driver_path = os.environ.get('CHROMEDRIVER_PATH')

        chrome_options = webdriver.ChromeOptions() 
        #chrome_options.binary_location = chrome_bin_path
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-sh-usage')
        
        chrome_driver_path = 'chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=chrome_driver_path,chrome_options=chrome_options)
        
    def setup_telegram_bot(self):
        self.tgbot = TGBot(self,self.TELEGRAM_BOT_TOKEN,self.TELEGRAM_BOT_VERIFICATIONCODE)

    def __init__(self):
        try:
            self.grades = {}
            self.configuration()
            self.setup_telegram_bot()
            self.setup_selenium()
            self.run_first_time()
        except:
            print('Error occurred in constructor, program will terminate')
            sys.exit()
        self.run_loop()

    def get_grades(self):
        tbody = self.driver.find_elements_by_tag_name('tbody')[6] # 7th element is the grade table
        tr = tbody.find_elements_by_tag_name('tr')
        result = []
        for row in tr:
            list = []
            for td in row.find_elements_by_tag_name('td'):
                for font in td.find_elements_by_tag_name('font'):
                    list.append(font.text)
            if len(list)==5:
                result.append(list)
        result = result[1:]
        returngrades = {}
        for course in result:
            returngrades[course[0]] = course[3]
        return returngrades
    
    def refresh(self):
        self.driver.find_element_by_xpath("//*[contains(text(), 'Student Record')]").click()
        time.sleep(3)
        self.driver.find_element_by_xpath("//*[contains(text(), 'My Academic Record')]").click()
        time.sleep(3)
        self.driver.find_element_by_xpath("//*[contains(text(), 'Grade Display')]").click()
        time.sleep(3)
        self.driver.find_elements_by_xpath(".//input[@value='Go' and @type='submit']")[1].click()
        time.sleep(3)

    def run_first_time(self):
        try:
            self.driver.get(self.CITYU_AIMS_URL)
            time.sleep(5) # allow time to redirect
            self.driver.find_element_by_id('okta-signin-username').send_keys(self.EID)
            self.driver.find_element_by_id('okta-signin-password').send_keys(self.PASSWORD)
            self.driver.find_element_by_id('okta-signin-submit').click()
            time.sleep(10)

            self.refresh()

            result = self.get_grades()
            self.grades = result
            print(self.grades)
            self.notify()
        except:
            print('Error occurred in run_first_time(), will retry after 10 seconds')
            time.sleep(10)
            self.run_first_time()

    def run_loop(self):
        while True:
            try:
                self.check_grade_update()
                time.sleep(self.CRAWL_INTERVAL)
            except:
                print('Error occurred in run_loop(), will retry run_first_time() after 10 seconds')
                time.sleep(10)
                self.run_first_time()

    def check_grade_update(self):
        self.refresh()
        
        new_grades = self.get_grades()
        print(datetime.now(),new_grades)
        updated = False
        for course in new_grades:
            if course in self.grades:
                if new_grades[course] != self.grades[course]:
                    updated = True
        self.grades = new_grades
        if updated:
            self.notify(True)

    def get_grades_text(self):
        if len(self.grades)==0:
            return 'Current grade not available!\nThe bot may need some time to initialize(around 1 minute), you will receive a confirm message soon.\nIf you cannot receive any message later, you may report to the author.'
        graded = []
        inprogress = []
        for course in self.grades:
            if self.grades[course] == 'In Progress':
                inprogress.append(course)
            else:
                graded.append(course)
        text = 'Current Grades\n'
        text += 'Graded:\n'
        for course in graded:
            text += course + '\t' + self.grades[course] + '\n'
        text += '\n'
        text += 'In Progress:\n'
        for course in inprogress:
            text += course + '\t' + self.grades[course] + '\n'
        return text

    def notify(self, updated=False):
        try:
            self.tgbot.notify(updated)
        except:
            print('Error with tgbot!')

class TGBot:
    def __init__(self, grade_checker: GradeChecker, bot_token: str, verifycation_code: str):
        self.grade_checker = grade_checker
        self.TELEGRAM_BOT_TOKEN = bot_token
        self.TELEGRAM_BOT_VERIFICATIONCODE = verifycation_code
        self.TELEGRAM_BOT_VERIFIED_LIST = []
        self.updater = Updater(token=self.TELEGRAM_BOT_TOKEN)
        dispatcher = self.updater.dispatcher
        start_handler = CommandHandler('start',self.bot_start)
        dispatcher.add_handler(start_handler)
        verify_handler = CommandHandler('verify',self.bot_verify)
        dispatcher.add_handler(verify_handler)
        self.updater.start_polling()
        
    
    def bot_start(self,update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Telegram Bot is running!')

    def bot_verify(self,update: Update, context: CallbackContext,args=None):
            for arg in context.args:
                if arg == self.TELEGRAM_BOT_VERIFICATIONCODE:
                    chatid = update.effective_chat.id
                    if chatid not in self.TELEGRAM_BOT_VERIFIED_LIST:
                        self.TELEGRAM_BOT_VERIFIED_LIST.append(chatid)
                        context.bot.send_message(chat_id=chatid, text='Verification code is correct! Added to notify list.\n')
                    else:
                        context.bot.send_message(chat_id=chatid, text='Already verified!\n')
                    context.bot.send_message(chat_id=chatid, text=self.grade_checker.get_grades_text())
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text='Verification code is incorrect! Please retry.')
                break

    def notify(self,updated=False):
        for user in self.TELEGRAM_BOT_VERIFIED_LIST:
            if updated:
                self.updater.bot.sendMessage(chat_id=user,text='Grade updated!!!')
            else:
                self.updater.bot.sendMessage(chat_id=user,text='Initialization completed.')
            self.updater.bot.sendMessage(chat_id=user,text=self.grade_checker.get_grades_text())
    
def main():
    instance = GradeChecker()

if __name__ == '__main__':
    main()
