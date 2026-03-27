"""
登录页面类
使用 POM（Page Object Model）设计模式
网站：https://dev.aigrowth8.com/login
"""
from playwright.sync_api import Page
from playwright.sync_api import expect
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
        """错误提示信息 - 兼容弹窗提示和表单错误提示"""
        return self.page.locator(
            ".ant-message-error, .ant-form-item-explain-error"
        )

    # ==================== 页面操作方法 ====================

    @allure.step("导航到登录页面")
    def navigate(self, base_url: str):
        """
        导航到登录页面

        Args:
            base_url: 网站基础 URL
        """
        login_url = f"{base_url}/login"
        self.page.goto(login_url, wait_until="domcontentloaded")
        self.phone_input.wait_for(state="visible")

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
    def click_login_button(self, force: bool = False):
        """点击登录按钮"""
        self.login_button.click(force=force)

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

    @allure.step("验证登录页面加载完成")
    def verify_login_page_loaded(self):
        """验证登录页关键元素可见"""
        expect(self.phone_input).to_be_visible()
        expect(self.password_input).to_be_visible()
        expect(self.login_button).to_be_visible()

    @allure.step("验证是否显示错误信息")
    def is_error_message_displayed(self, timeout: int = 5000) -> bool:
        """检查是否出现错误提示"""
        try:
            expect(self.error_message.first).to_be_visible(timeout=timeout)
            return True
        except AssertionError:
            return False
