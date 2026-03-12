"""
成员管理页面类
使用 POM（Page Object Model）设计模式
网站：https://dev.aigrowth8.com
"""
from playwright.sync_api import Page
import allure


class MemberManagementPage:
    """
    成员管理页面操作类
    封装成员管理页面的所有元素和操作方法
    """

    def __init__(self, page: Page):
        """
        初始化成员管理页面

        Args:
            page: Playwright Page 对象
        """
        self.page = page

    # ==================== 页面元素定位器 ====================

    @property
    def account_management_link(self):
        """账号管理链接 - 使用 get_by_role 定位"""
        return self.page.get_by_role("link", name="账号管理")

    @property
    def add_member_button(self):
        """添加成员按钮 - 使用 get_by_role 定位"""
        return self.page.get_by_role("button", name="plus 添加成员")

    @property
    def phone_search_input(self):
        """手机号搜索输入框 - 使用 get_by_role 定位"""
        return self.page.get_by_role("textbox", name="请输入手机号搜索")

    @property
    def member_checkbox(self):
        """成员复选框 - 使用 get_by_role 定位"""
        return self.page.get_by_role("checkbox", name="赵文龙")

    @property
    def confirm_button(self):
        """确定按钮 - 使用 get_by_role 定位"""
        return self.page.get_by_role("button", name="确 定")

    @property
    def success_message(self):
        """成功提示信息 - 使用 get_by_text 定位"""
        return self.page.get_by_text("成功添加 1 名成员")

    # ==================== 页面操作方法 ====================

    @allure.step("点击账号管理链接")
    def click_account_management(self):
        """点击账号管理链接"""
        self.account_management_link.wait_for(state="visible")
        self.account_management_link.click()

    @allure.step("点击添加成员按钮")
    def click_add_member(self):
        """点击添加成员按钮"""
        self.add_member_button.wait_for(state="visible")
        self.add_member_button.click()

    @allure.step("输入手机号搜索：{phone}")
    def input_phone_search(self, phone: str):
        """
        输入手机号搜索

        Args:
            phone: 手机号码
        """
        self.phone_search_input.wait_for(state="visible")
        self.phone_search_input.clear()
        self.phone_search_input.fill(phone)

    @allure.step("勾选成员复选框")
    def check_member(self):
        """勾选成员复选框"""
        self.member_checkbox.wait_for(state="visible")
        self.member_checkbox.check()

    @allure.step("点击确定按钮")
    def click_confirm(self):
        """点击确定按钮"""
        self.confirm_button.wait_for(state="visible")
        self.confirm_button.click()

    @allure.step("执行添加成员操作")
    def add_member(self, phone: str):
        """
        执行完整的添加成员流程

        Args:
            phone: 要搜索的手机号码
        """
        self.click_account_management()
        self.click_add_member()
        self.input_phone_search(phone)
        self.check_member()
        self.click_confirm()
