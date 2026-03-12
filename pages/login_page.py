"""
登录页面类
使用 POM（Page Object Model）设计模式
网站：https://dev.aigrowth8.com/login
"""
from playwright.sync_api import Page
import allure


class LoginPage:
    """
    登录页面操作类
    封装登录页面的所有元素和操作方法
    """

    def __init__(self, page: Page):
        """
        初始化登录页面

        Args:
            page: Playwright Page 对象
        """
        self.page = page

    # ==================== 页面元素定位器 ====================

    @property
    def phone_input(self):
        """手机号码输入框 - 使用 get_by_placeholder 定位"""
        return self.page.get_by_placeholder("请输入手机号码")

    @property
    def password_input(self):
        """密码输入框 - 使用 get_by_placeholder 定位"""
        return self.page.get_by_placeholder("请输入密码")

    @property
    def login_button(self):
        """登录按钮 - 使用 get_by_role 定位"""
        return self.page.get_by_role("button", name="登录系统")

    @property
    def error_message(self):
        """错误提示信息 - 使用 CSS 定位（Element UI 消息组件）"""
        return self.page.locator(".ant-message-error")

    # ==================== 页面操作方法 ====================

    @allure.step("导航到登录页面")
    def navigate(self, base_url: str):
        """
        导航到登录页面

        Args:
            base_url: 网站基础 URL
        """
        login_url = f"{base_url}/login"
        self.page.goto(login_url)
        self.page.wait_for_load_state("networkidle")

    @allure.step("输入手机号码：{phone}")
    def input_phone(self, phone: str):
        """
        输入手机号码

        Args:
            phone: 手机号码
        """
        self.phone_input.wait_for(state="visible")
        self.phone_input.click()
        self.phone_input.clear()
        self.phone_input.fill(phone)

    @allure.step("输入密码")
    def input_password(self, password: str):
        """
        输入密码

        Args:
            password: 密码
        """
        self.password_input.wait_for(state="visible")
        self.password_input.click()
        self.password_input.clear()
        self.password_input.fill(password)

    @allure.step("点击登录按钮")
    def click_login_button(self):
        """点击登录按钮"""
        self.login_button.click()

    @allure.step("执行登录操作")
    def login(self, phone: str, password: str):
        """
        执行完整的登录流程

        Args:
            phone: 手机号码
            password: 密码
        """
        self.input_phone(phone)
        self.input_password(password)
        self.click_login_button()
