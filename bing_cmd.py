import random
import time
import os
import sys
import subprocess
import winreg
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_base_path():
    """獲取程式的基礎路徑，適用於exe和py檔案"""
    if getattr(sys, 'frozen', False):
        # 如果是打包後的exe檔案
        return os.path.dirname(sys.executable)
    else:
        # 如果是原始Python腳本
        return os.path.dirname(os.path.abspath(__file__))

def find_browser_executable(browser_name):
    """自動尋找瀏覽器執行檔路徑"""
    browser_paths = {
        'chrome': [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ],
        'firefox': [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe")
        ],
        'edge': [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ],
        'brave': [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
        ],
        'opera': [
            r"C:\Users\{}\AppData\Local\Programs\Opera\opera.exe".format(os.getenv('USERNAME')),
            r"C:\Program Files\Opera\opera.exe",
            r"C:\Program Files (x86)\Opera\opera.exe"
        ]
    }
    
    # 檢查常見路徑
    if browser_name.lower() in browser_paths:
        for path in browser_paths[browser_name.lower()]:
            if os.path.exists(path):
                return path
    
    # 嘗試從註冊表找（Windows）
    try:
        if browser_name.lower() == 'chrome':
            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
            ]
        elif browser_name.lower() == 'firefox':
            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe"
            ]
        elif browser_name.lower() == 'brave':
            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\brave.exe",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\brave.exe"
            ]
        else:
            reg_paths = []
        
        for reg_path in reg_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    path = winreg.QueryValue(key, "")
                    if os.path.exists(path):
                        return path
            except:
                continue
                
    except Exception as e:
        print(f"註冊表查詢失敗: {e}")
    
    return None

class BingSearchAutomation:
    def __init__(self):
        self.search_queries = [
            "天氣預報", "新聞頭條", "股市行情", "美食推薦", "旅遊景點",
            "電影評論", "音樂推薦", "運動新聞", "科技資訊", "健康知識",
            "學習資源", "購物優惠", "交通資訊", "生活小貼士", "娛樂新聞",
            "財經資訊", "教育資源", "文化活動", "環保知識", "時尚潮流",
            "程式設計", "數據分析", "人工智慧", "機器學習", "雲端計算"
        ]
        
    def setup_chrome_driver(self, mobile=False, browser_executable=None):
        """設置Chrome瀏覽器（也適用於Brave和Opera）"""
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 設置自定義瀏覽器執行檔路徑
        if browser_executable:
            options.binary_location = browser_executable
            print(f"✓ 使用自定義瀏覽器路徑: {browser_executable}")
        
        if mobile:
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # 使用程式目錄中的chromedriver
        chromedriver_path = os.path.join(get_base_path(), "chromedriver.exe")
        
        if os.path.exists(chromedriver_path):
            service = ChromeService(chromedriver_path)
            print(f"✓ 找到 chromedriver.exe: {chromedriver_path}")
        else:
            print(f"❌ 未找到 chromedriver.exe: {chromedriver_path}")
            return None
            
        try:
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Chrome驅動啟動失敗: {e}")
            return None
    
    def setup_firefox_driver(self, mobile=False):
        """設置Firefox瀏覽器"""
        options = webdriver.FirefoxOptions()
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference("browser.startup.homepage", "about:blank")
        options.set_preference("startup.homepage_welcome_url", "about:blank")
        options.set_preference("startup.homepage_welcome_url.additional", "about:blank")
        
        # 查找Firefox執行檔
        firefox_path = find_browser_executable('firefox')
        if firefox_path:
            options.binary_location = firefox_path
            print(f"✓ 找到Firefox: {firefox_path}")
        else:
            print("⚠ 未找到Firefox執行檔，嘗試使用系統預設路徑")
        
        if mobile:
            options.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1")
        
        # 使用程式目錄中的geckodriver
        geckodriver_path = os.path.join(get_base_path(), "geckodriver.exe")
        
        if os.path.exists(geckodriver_path):
            service = FirefoxService(geckodriver_path)
            print(f"✓ 找到 geckodriver.exe: {geckodriver_path}")
        else:
            print(f"❌ 未找到 geckodriver.exe: {geckodriver_path}")
            return None
        
        try:
            driver = webdriver.Firefox(service=service, options=options)
            return driver
        except Exception as e:
            print(f"Firefox驅動啟動失敗: {e}")
            return None
    
    def setup_edge_driver(self, mobile=False):
        """設置Edge瀏覽器"""
        options = webdriver.EdgeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 查找Edge執行檔
        edge_path = find_browser_executable('edge')
        if edge_path:
            options.binary_location = edge_path
            print(f"✓ 找到Edge: {edge_path}")
        
        if mobile:
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # 使用程式目錄中的msedgedriver
        edgedriver_path = os.path.join(get_base_path(), "msedgedriver.exe")
        
        if os.path.exists(edgedriver_path):
            service = EdgeService(edgedriver_path)
            print(f"✓ 找到 msedgedriver.exe: {edgedriver_path}")
        else:
            print(f"❌ 未找到 msedgedriver.exe: {edgedriver_path}")
            return None
        
        try:
            driver = webdriver.Edge(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Edge驅動啟動失敗: {e}")
            return None
    
    def get_driver(self, browser_name, mobile=False):
        """根據瀏覽器名稱獲取對應的driver - 修正版本"""
        browser_name = browser_name.lower()
        print(f"\n正在啟動 {browser_name.upper()} {'(手機模式)' if mobile else '(桌面模式)'}...")
        
        try:
            if browser_name == 'chrome':
                chrome_path = find_browser_executable('chrome')
                if not chrome_path:
                    print("❌ 未找到Chrome執行檔")
                    return None
                driver = self.setup_chrome_driver(mobile, chrome_path)
                
            elif browser_name == 'firefox':
                driver = self.setup_firefox_driver(mobile)
                
            elif browser_name == 'edge':
                driver = self.setup_edge_driver(mobile)
                
            elif browser_name == 'brave':
                brave_path = find_browser_executable('brave')
                if not brave_path:
                    print("❌ 未找到Brave執行檔")
                    print("請確保已安裝Brave瀏覽器")
                    return None
                driver = self.setup_chrome_driver(mobile, brave_path)
                
            elif browser_name == 'opera':
                opera_path = find_browser_executable('opera')
                if not opera_path:
                    print("❌ 未找到Opera執行檔")
                    print("請確保已安裝Opera瀏覽器")
                    return None
                driver = self.setup_chrome_driver(mobile, opera_path)
                
            else:
                raise ValueError(f"不支持的瀏覽器: {browser_name}")
            
            if driver is None:
                print(f"❌ 無法啟動 {browser_name} 瀏覽器")
                return None
            
            # 設置窗口大小
            if not mobile:
                driver.set_window_size(1920, 1080)
            
            print(f"✓ {browser_name.upper()} 啟動成功")
            return driver
            
        except Exception as e:
            print(f"❌ 啟動 {browser_name} 時發生錯誤: {e}")
            return None
    
    def perform_search(self, driver, query):
        """執行搜索操作 - 增強版本"""
        if driver is None:
            print("❌ Driver是None，無法執行搜索")
            return False
            
        try:
            # 前往Bing首頁
            driver.get("https://www.bing.com")
            time.sleep(random.uniform(3, 5))
            
            # 找到搜索框並輸入查詢
            search_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            # 清空搜索框
            search_box.clear()
            time.sleep(random.uniform(0.5, 1))
            
            # 模擬人類輸入
            for char in query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.08, 0.2))
            
            # 按Enter搜索
            time.sleep(random.uniform(1, 2))
            search_box.send_keys(Keys.ENTER)
            
            # 等待搜索結果載入
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "b_results"))
            )
            
            # 隨機滾動頁面
            for _ in range(random.randint(2, 4)):
                scroll_height = random.randint(200, 600)
                driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(random.uniform(1, 2))
            
            # 30%機率點擊搜索結果
            if random.random() < 0.3:
                try:
                    results = driver.find_elements(By.CSS_SELECTOR, "#b_results .b_algo h2 a")
                    if results:
                        result_to_click = random.choice(results[:5])
                        result_to_click.click()
                        time.sleep(random.uniform(3, 6))
                        driver.back()
                        time.sleep(random.uniform(1, 2))
                except Exception as e:
                    print(f"點擊搜索結果時出錯: {e}")
            
            time.sleep(random.uniform(1, 3))
            return True
            
        except Exception as e:
            print(f"搜索 '{query}' 時發生錯誤: {e}")
            return False
    
    def login_to_bing_rewards(self, driver):
        """登入Bing Rewards - 改進版本"""
        try:
            print("正在前往Bing Rewards...")
            driver.get("https://rewards.bing.com/dashboard")
            time.sleep(5)
            
            # 檢查當前URL
            current_url = driver.current_url
            
            # 如果需要登入
            if "login" in current_url.lower() or "signin" in current_url.lower():
                print("⚠ 需要登入Microsoft帳號")
                print("請在瀏覽器中完成登入，然後...")
                input("登入完成後按Enter繼續...")
                
                # 重新載入頁面
                driver.get("https://rewards.bing.com/dashboard")
                time.sleep(3)
            
            # 檢查是否成功進入
            time.sleep(3)
            final_url = driver.current_url
            
            if "rewards.bing.com" in final_url and "dashboard" in final_url:
                print("✓ 成功進入Bing Rewards儀表板")
                return True
            else:
                print("⚠ 可能未成功登入，但繼續執行...")
                return False
            
        except Exception as e:
            print(f"登入Bing Rewards時發生錯誤: {e}")
            return False
    
    def complete_daily_tasks(self, driver):
        """完成每日任務 - 改進版本"""
        try:
            print("正在尋找可完成的任務...")
            time.sleep(3)
            
            # 多種選擇器尋找任務
            task_selectors = [
                ".rewards-card-container",
                ".daily-sets .ds-card-sec", 
                ".more-activities .ds-card-sec",
                "[data-bi-id*='task']",
                ".offer-card"
            ]
            
            completed_tasks = 0
            max_tasks = 3
            
            for selector in task_selectors:
                try:
                    tasks = driver.find_elements(By.CSS_SELECTOR, selector)
                    if not tasks:
                        continue
                    
                    print(f"找到 {len(tasks)} 個潛在任務")
                    
                    for i, task in enumerate(tasks[:max_tasks]):
                        try:
                            if not task.is_displayed():
                                continue
                            
                            # 滾動到任務元素
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", task)
                            time.sleep(2)
                            
                            # 嘗試點擊任務
                            try:
                                task.click()
                            except:
                                driver.execute_script("arguments[0].click();", task)
                            
                            print(f"✓ 點擊任務 {completed_tasks + 1}")
                            time.sleep(random.uniform(3, 5))
                            completed_tasks += 1
                            
                            # 處理新視窗
                            original_window = driver.current_window_handle
                            if len(driver.window_handles) > 1:
                                for handle in driver.window_handles:
                                    if handle != original_window:
                                        driver.switch_to.window(handle)
                                        time.sleep(2)
                                        driver.close()
                                driver.switch_to.window(original_window)
                            
                            # 回到主頁面
                            if driver.current_url != "https://rewards.bing.com/dashboard":
                                driver.get("https://rewards.bing.com/dashboard")
                                time.sleep(3)
                            
                            if completed_tasks >= max_tasks:
                                break
                                
                        except Exception as e:
                            print(f"處理任務時出錯: {e}")
                            continue
                    
                    if completed_tasks >= max_tasks:
                        break
                        
                except Exception as e:
                    print(f"使用選擇器 {selector} 時出錯: {e}")
                    continue
            
            print(f"✓ 完成 {completed_tasks} 個任務")
            return completed_tasks > 0
            
        except Exception as e:
            print(f"完成每日任務時發生錯誤: {e}")
            return False
    
    def run_automation(self, browsers=['edge', 'chrome', 'firefox', 'brave', 'opera'], desktop_search_count=30, mobile_search_count=20, enable_mobile_search=True):
        """運行自動化腳本 - 改進版本"""
        print("🚀 開始Bing搜索自動化...")
        print(f"📊 設定: 桌面搜索{desktop_search_count}次, 手機搜索{mobile_search_count}次")
        print("=" * 60)
        
        total_success = 0
        
        for browser_index, browser in enumerate(browsers):
            print(f"\n{'='*50}")
            print(f"[{browser_index + 1}/{len(browsers)}] 正在使用 {browser.upper()} 瀏覽器")
            print(f"{'='*50}")
            
            # 桌面版搜索
            desktop_driver = None
            try:
                desktop_driver = self.get_driver(browser, mobile=False)
                if desktop_driver is None:
                    print(f"❌ 跳過 {browser} 桌面版 - 瀏覽器啟動失敗")
                else:
                    print(f"✓ {browser.upper()} 桌面版啟動成功")
                    
                    # 登入並完成任務
                    if self.login_to_bing_rewards(desktop_driver):
                        self.complete_daily_tasks(desktop_driver)
                    
                    # 執行桌面搜索
                    desktop_success = 0
                    print(f"\n開始桌面搜索 ({desktop_search_count} 次)...")
                    
                    for i in range(desktop_search_count):
                        query = random.choice(self.search_queries)
                        print(f"[{i+1}/{desktop_search_count}] 搜索: {query}")
                        
                        if self.perform_search(desktop_driver, query):
                            desktop_success += 1
                        
                        # 進度報告
                        if (i + 1) % 5 == 0:
                            print(f"  進度: {i+1}/{desktop_search_count} (成功: {desktop_success})")
                        
                        # 等待時間
                        if i < desktop_search_count - 1:
                            wait_time = random.uniform(4, 8)
                            time.sleep(wait_time)
                    
                    print(f"✓ 桌面搜索完成: {desktop_success}/{desktop_search_count} 成功")
                    total_success += desktop_success
                
            except Exception as e:
                print(f"❌ 桌面版 {browser} 發生錯誤: {e}")
            finally:
                if desktop_driver:
                    try:
                        desktop_driver.quit()
                    except:
                        pass
            
            # 手機版搜索
            if enable_mobile_search:
                # 瀏覽器間休息
                print(f"\n⏳ 準備手機版搜索，休息30秒...")
                time.sleep(30)
                
                mobile_driver = None
                try:
                    mobile_driver = self.get_driver(browser, mobile=True)
                    if mobile_driver is None:
                        print(f"❌ 跳過 {browser} 手機版 - 瀏覽器啟動失敗")
                    else:
                        print(f"✓ {browser.upper()} 手機版啟動成功")
                        
                        # 手機版不需要登入Rewards，直接搜索
                        mobile_success = 0
                        print(f"\n開始手機搜索 ({mobile_search_count} 次)...")
                        
                        for i in range(mobile_search_count):
                            query = random.choice(self.search_queries)
                            print(f"[{i+1}/{mobile_search_count}] 手機搜索: {query}")
                            
                            if self.perform_search(mobile_driver, query):
                                mobile_success += 1
                            
                            # 進度報告
                            if (i + 1) % 5 == 0:
                                print(f"  進度: {i+1}/{mobile_search_count} (成功: {mobile_success})")
                            
                            # 等待時間
                            if i < mobile_search_count - 1:
                                wait_time = random.uniform(3, 6)
                                time.sleep(wait_time)
                        
                        print(f"✓ 手機搜索完成: {mobile_success}/{mobile_search_count} 成功")
                        total_success += mobile_success
                    
                except Exception as e:
                    print(f"❌ 手機版 {browser} 發生錯誤: {e}")
                finally:
                    if mobile_driver:
                        try:
                            mobile_driver.quit()
                        except:
                            pass
        
        print(f"\n{'='*60}")
        print("🎉 所有瀏覽器任務完成！")
        print(f"📊 總成功搜索次數: {total_success}")
        print(f"⏱ 程式執行完畢")
        print(f"{'='*60}")

def check_browser_installation():
    """檢查瀏覽器安裝狀態"""
    print("=== 檢查瀏覽器安裝狀態 ===")
    browsers = ['chrome', 'firefox', 'edge', 'brave', 'opera']
    available_browsers = []
    
    for browser in browsers:
        path = find_browser_executable(browser)
        if path:
            print(f"✓ {browser.upper()}: {path}")
            available_browsers.append(browser)
        else:
            print(f"❌ {browser.upper()}: 未安裝或無法找到")
    
    return available_browsers

def check_webdriver_files():
    """檢查WebDriver檔案"""
    print("\n=== 檢查WebDriver檔案 ===")
    base_path = get_base_path()
    
    webdrivers = {
        'chromedriver.exe': ['chrome', 'brave', 'opera'],
        'msedgedriver.exe': ['edge'],
        'geckodriver.exe': ['firefox']
    }
    
    available_drivers = []
    for driver_file, supported_browsers in webdrivers.items():
        driver_path = os.path.join(base_path, driver_file)
        if os.path.exists(driver_path):
            print(f"✓ {driver_file}: {driver_path}")
            available_drivers.extend(supported_browsers)
        else:
            print(f"❌ {driver_file}: 未找到")
    
    return available_drivers

def check_youtube_subscription():
    """檢查YouTube頻道訂閱狀態"""
    print("=== YouTube頻道訂閱檢查 ===")
    print("正在檢查是否已訂閱指定的YouTube頻道...")
    
    target_channel = "https://www.youtube.com/channel/UClPgyL87DKM5TN0gkU_aA5g"
    base_path = get_base_path()
    
    # 檢查可用的瀏覽器和驅動
    installed_browsers = check_browser_installation()
    available_drivers = check_webdriver_files()
    usable_browsers = list(set(installed_browsers) & set(available_drivers))
    
    if not usable_browsers:
        print("❌ 沒有可用的瀏覽器進行檢查")
        print("請先確保已安裝瀏覽器和對應的WebDriver檔案")
        choice = input("無法檢查訂閱狀態，是否繼續執行程式？(y/n): ").strip().lower()
        return choice in ['y', 'yes', '是', '']
    
    print(f"將使用以下瀏覽器檢查訂閱狀態: {', '.join([b.upper() for b in usable_browsers[:2]])}")  # 只用前兩個瀏覽器檢查
    
    subscription_found = False
    automation = BingSearchAutomation()
    
    for browser in usable_browsers[:2]:  # 限制只檢查前2個瀏覽器以節省時間
        print(f"\n正在使用 {browser.upper()} 檢查...")
        driver = None
        
        try:
            driver = automation.get_driver(browser, mobile=False)
            
            if driver is None:
                print(f"❌ 無法啟動 {browser}")
                continue
            
            # 前往YouTube頻道
            print(f"正在前往YouTube頻道...")
            driver.get(target_channel)
            time.sleep(5)
            
            # 檢查訂閱按鈕狀態
            try:
                # 等待頁面載入
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 多種方式查找訂閱相關元素
                subscription_selectors = [
                    "button[aria-label*='訂閱']",
                    "button[aria-label*='Subscribe']", 
                    "button[aria-label*='已訂閱']",
                    "button[aria-label*='Subscribed']",
                    "ytd-subscribe-button-renderer button",
                    "#subscribe-button button"
                ]
                
                button_found = False
                for selector in subscription_selectors:
                    try:
                        subscribe_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                        if subscribe_buttons:
                            button = subscribe_buttons[0]
                            button_text = button.get_attribute('aria-label') or button.text or ''
                            
                            # 檢查是否已訂閱
                            if any(keyword in button_text.lower() for keyword in ['已訂閱', 'subscribed', '訂閱中']):
                                print(f"✓ {browser.upper()}: 已訂閱此頻道 😊")
                                subscription_found = True
                                button_found = True
                                break
                            elif any(keyword in button_text.lower() for keyword in ['訂閱', 'subscribe']):
                                print(f"⚠ {browser.upper()}: 尚未訂閱此頻道 😢")
                                print("  請前往頻道按下訂閱鈕支持作者！")
                                button_found = True
                                break
                    except:
                        continue
                
                if not button_found:
                    print(f"? {browser.upper()}: 無法檢查訂閱狀態 (可能需要登入YouTube)")
                
            except Exception as e:
                print(f"⚠ {browser.upper()}: 檢查訂閱狀態時發生錯誤: {e}")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ {browser.upper()}: 啟動瀏覽器時發生錯誤: {e}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        # 瀏覽器之間稍作等待
        time.sleep(2)
    
    print(f"\n=== 訂閱檢查完成 ===")
    
    if subscription_found:
        print("✅ 在至少一個瀏覽器中發現已訂閱此頻道！")
        print("感謝您的支持！ 🎉")
    else:
        print("❌ 在所有檢查的瀏覽器中都未發現訂閱")
        print("請訂閱此頻道以支持作者的努力：")
        print(f"🔗 {target_channel}")
        print("\n訂閱後可以獲得更多實用工具和教學！")
        
        # 詢問是否要繼續
        choice = input("由於你沒有訂閱頻道，程式已結束，請自行關閉").strip().lower()
        
        if choice in ['n', 'no', '否']:
            print("程式已終止，請訂閱後再執行")
            return False
    
    print("繼續執行主程式...\n")
    return True

def get_user_settings():
    """獲取用戶設定"""
    print("\n=== 設定搜索參數 ===")

    # 檢查可用的瀏覽器和驅動
    installed_browsers = check_browser_installation()
    available_drivers = check_webdriver_files()

    # 保持固定順序，且同時具備安裝與對應 WebDriver
    preferred_order = ['edge', 'chrome', 'firefox', 'brave', 'opera']
    usable_browsers = [b for b in preferred_order if (b in installed_browsers and b in available_drivers)]

    if not usable_browsers:
        print("\n❌ 沒有可用的瀏覽器！")
        print("請確保：")
        print("1. 已安裝瀏覽器")
        print("2. 已下載對應的 WebDriver 檔案 (與程式同資料夾)")
        return None, 0, 0, False

    print(f"\n可用的瀏覽器: {', '.join([b.upper() for b in usable_browsers])}")

    # 瀏覽器選擇
    print("\n瀏覽器選擇:")
    for i, browser in enumerate(usable_browsers, 1):
        print(f"{i}. {browser.upper()}")
    print(f"{len(usable_browsers) + 1}. 全部使用")

    while True:
        choice = input(f"請選擇 (1-{len(usable_browsers) + 1}，預設全部): ").strip()
        if not choice or choice == str(len(usable_browsers) + 1):
            selected_browsers = usable_browsers
            break
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(usable_browsers):
                selected_browsers = [usable_browsers[choice_num - 1]]
                break
            else:
                print("請輸入有效的選擇")
        except ValueError:
            print("請輸入有效的數字")

    # 桌面搜索次數
    while True:
        desktop_count_input = input("桌面搜索次數 (預設30): ").strip()
        if not desktop_count_input:
            desktop_count = 30
            break
        try:
            desktop_count = int(desktop_count_input)
            if desktop_count >= 0:
                break
            else:
                print("請輸入 0 或更大的整數")
        except ValueError:
            print("請輸入有效的數字")

    # 手機搜索次數
    while True:
        mobile_count_input = input("手機搜索次數 (預設20): ").strip()
        if not mobile_count_input:
            mobile_count = 20
            break
        try:
            mobile_count = int(mobile_count_input)
            if mobile_count >= 0:
                break
            else:
                print("請輸入 0 或更大的整數")
        except ValueError:
            print("請輸入有效的數字")

    # 是否啟用手機搜索
    while True:
        mobile_enable_input = input("是否啟用手機搜索？(y/n，預設 y): ").strip().lower()
        if mobile_enable_input in ["", "y", "yes", "是"]:
            enable_mobile_search = True
            break
        elif mobile_enable_input in ["n", "no", "否"]:
            enable_mobile_search = False
            break
        else:
            print("請輸入 y 或 n")

    return selected_browsers, desktop_count, mobile_count, enable_mobile_search


# —— 建議同步強化搜尋框 selector（在 perform_search 內替換這段）——
# 原本：
# search_box = WebDriverWait(driver, 15).until(
#     EC.presence_of_element_located((By.NAME, "q"))
# )
# 建議改成：
# search_box = WebDriverWait(driver, 15).until(
#     EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q'], #sb_form_q"))
# )


if __name__ == "__main__":
    # 先進行 YouTube 訂閱檢查（回傳 False 則結束）
    if not check_youtube_subscription():
        sys.exit(0)

    # 互動式取得使用者設定
    browsers, desktop_count, mobile_count, enable_mobile_search = get_user_settings()
    if not browsers:
        sys.exit(1)

    # 依設定執行主流程
    automation = BingSearchAutomation()
    automation.run_automation(
        browsers=browsers,
        desktop_search_count=desktop_count,
        mobile_search_count=mobile_count,
        enable_mobile_search=enable_mobile_search
    )
