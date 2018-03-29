from selenium import webdriver
from scrapy.selector import Selector
browser = webdriver.Chrome(executable_path="E:/SE/chromedriver.exe")

browser.get("https://www.zhihu.com/signup?next=%2F#signin")

#print(browser.page_source)
browser.find_element_by_css_selector(".SignFlow-accountInput input[name='username']").send_keys("18550821934")
browser.find_element_by_css_selector(".Input-wrapper input[name='password']").send_keys("wangsw101183")

browser.find_element_by_css_selector(".view-siginin button.sign-button").click()

browser.execute_script("window.scrollTo(0,document.body.scrollHeight); var lenofPage=document.body.scrollHeight; return lenofPage")

# selector = Selector(text=browser.page_source)
# selector.css()


#设置不加载图片
chrome = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chrome.add_experimental_option("prefs",prefs)
browser = webdriver.Chrome(executable_path="E:/SE/chromedriver.exe",chrome_options=chrome)

#phantomjs 无界面浏览器 多进程性能下降严重


browser.quit()