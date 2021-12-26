# CityU Grade Checker

![image](https://user-images.githubusercontent.com/42265526/147413336-a9ea5ffb-5553-47ac-995c-98e0e9d0831c.png)

This is a python script for automatic notification of CityU AIMS grade updates with telegram bot.

## Disclaimer: 

This script is still under development. 

The author is not a staff of City University of Hong Kong. Use at your own discretion.

## Usage

1. Install required packages
```
pip3 install selenium python-telegram-bot
```

2. Install chrome driver
Download from here https://chromedriver.chromium.org/downloads if you are using windows or mac

Visit https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/ for details if you are using ubuntu

1. Create a new telegram bot
Goto https://telegram.me/BotFather and execute 
```
/newbot
```   
Follow the instructions to create a telegram bot, keep the link to the bot and save the token to access the HTTP API, that is the telegram bot token for later use

4. Configure the script

Configuration can be done in these two functions

```
   def configuration(self):
        self.EID = 'myeid' # set to your login eid
        self.PASSWORD = 'mypassword' # set to your login password
        self.TELEGRAM_BOT_TOKEN = 'mybottoken' # set to your telegram bot token from step 3
        self.TELEGRAM_BOT_VERIFICATIONCODE = 'secret' # this is used to verify you with your telegram bot, you can think a new random password here
        self.CITYU_AIMS_URL = 'http://www.cityu.edu.hk/cityu/qlink/aims.htm' # do not change this
        self.CRAWL_INTERVAL = 30 # crawl interval in second, you can try to set a different value 


    def setup_selenium(self):
        # You can uncomment the lines to do some setup if needed

        # chrome_bin_path = os.environment.get('GOOGLE_CHROME_BIN')
        # chrome_driver_path = os.environ.get('CHROMEDRIVER_PATH')

        chrome_options = webdriver.ChromeOptions() 
        #chrome_options.binary_location = chrome_bin_path
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-sh-usage')
        
        chrome_driver_path = 'chromedriver.exe' # set this to your chrome driver path
        self.driver = webdriver.Chrome(executable_path=chrome_driver_path,chrome_options=chrome_options)
        
```

5. Execute the script
```
python3 main.py
```

6. Access the telegram bot created earlier

You can access your bot and type

```
/verify <verification_code>
```

For example, if you set self.TELEGRAM_BOT_VERIFICATIONCODE = 'secret' in main.py, you can do

```
/verify secret
```

If everything works fine, you will receive grade update from your telegram bot
