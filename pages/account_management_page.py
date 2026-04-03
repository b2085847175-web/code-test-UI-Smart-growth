"""
账号管理页面类
负责账号管理相关操作（搜索、新增、添加成员等）
"""
import re

from playwright.sync_api import Page
import allure


class AccountManagementPage:
    """
    账号管理页面操作类
    """

    def __init__(self, page: Page):
        self.page = page

    @property
    def account_management_link(self):
        return self.page.get_by_role("link", name="账号管理")

    # ==================== 新增账号相关元素 ====================

    @property
    def add_account_button(self):
        return self.page.get_by_role("button", name=re.compile(r"(新增账号|添加账号)"))

    @property
    def add_account_dialog(self):
        return self.page.get_by_role("dialog").last

    @property
    def account_name_input(self):
        return self.add_account_dialog.get_by_placeholder("请输入员工姓名")

    @property
    def account_password_input(self):
        return self.add_account_dialog.get_by_placeholder("请输入密码")

    @property
    def account_phone_input(self):
        return self.add_account_dialog.get_by_placeholder("请输入手机号")

    @property
    def role_selector(self):
        return self.add_account_dialog.get_by_label("角色")

    @property
    def identity_type_selector(self):
        return self.add_account_dialog.get_by_label("身份类型")

    @property
    def save_account_button(self):
        return self.add_account_dialog.get_by_role("button", name=re.compile(r"保\s*存"))

    # ==================== 账号列表搜索框（两个输入框） ====================

    @property
    def list_phone_search_input(self):
        return self.page.get_by_placeholder("根据手机号搜索")

    @property
    def list_name_search_input(self):
        return self.page.get_by_placeholder("根据姓名搜索")

    # ==================== 添加成员相关元素 ====================

    @property
    def add_member_button(self):
        return self.page.get_by_role("button", name=re.compile(r"添加成员"))

    @property
    def member_phone_search_input(self):
        return self.page.get_by_placeholder("请输入手机号搜索")

    @property
    def member_checkbox(self):
        return self.page.locator(".ant-modal-body .ant-checkbox-input").first

    @property
    def confirm_button(self):
        return self.page.get_by_role("button", name=re.compile(r"确\s*定"))

    @property
    def success_message(self):
        return self.page.get_by_text("成功添加")

    @property
    def no_member_message(self):
        return self.page.get_by_text("未找到匹配的成员")

    # ==================== 新增账号相关方法 ====================

    @allure.step("点击新增账号按钮")
    def click_add_account(self):
        self.add_account_button.wait_for(state="visible")
        self.add_account_button.click()

    @allure.step("输入员工姓名：{name}")
    def input_account_name(self, name: str):
        self.account_name_input.wait_for(state="visible")
        self.account_name_input.click()
        self.account_name_input.clear()
        self.account_name_input.fill(name)

    @allure.step("输入账号密码")
    def input_account_password(self, password: str):
        self.account_password_input.wait_for(state="visible")
        self.account_password_input.click()
        self.account_password_input.clear()
        self.account_password_input.fill(password)

    @allure.step("输入手机号：{phone}")
    def input_account_phone(self, phone: str):
        self.account_phone_input.wait_for(state="visible")
        self.account_phone_input.click()
        self.account_phone_input.clear()
        self.account_phone_input.fill(phone)

    @allure.step("选择角色：{role}")
    def select_role(self, role: str):
        self.role_selector.click()
        self.page.get_by_title(role).first.click()

    @allure.step("选择身份类型：{identity_type}")
    def select_identity_type(self, identity_type: str):
        self.identity_type_selector.click()
        self.page.get_by_text(identity_type).first.click()

    @allure.step("点击保存账号")
    def click_save_account(self):
        self.save_account_button.wait_for(state="visible")
        self.save_account_button.click()

    @allure.step("执行新增账号操作")
    def create_account(
        self,
        name: str,
        password: str,
        phone: str,
        role: str = "普通成员",
        identity_type: str = "内部用户"
    ):
        self.click_account_management()
        self.click_add_account()
        self.input_account_name(name)
        self.input_account_password(password)
        self.input_account_phone(phone)
        self.select_role(role)
        self.select_identity_type(identity_type)
        self.click_save_account()

    # ==================== 账号列表搜索框方法 ====================

    @allure.step("点击手机号搜索输入框")
    def click_list_phone_search_input(self):
        self.list_phone_search_input.wait_for(state="visible")
        self.list_phone_search_input.click()

    @allure.step("输入手机号搜索关键字：{phone}")
    def input_list_phone_search(self, phone: str):
        self.list_phone_search_input.wait_for(state="visible")
        self.list_phone_search_input.click()
        self.list_phone_search_input.fill(phone)

    @allure.step("点击姓名搜索输入框")
    def click_list_name_search_input(self):
        self.list_name_search_input.wait_for(state="visible")
        self.list_name_search_input.click()

    @allure.step("输入姓名搜索关键字：{name}")
    def input_list_name_search(self, name: str):
        self.list_name_search_input.wait_for(state="visible")
        self.list_name_search_input.click()
        self.list_name_search_input.fill(name)

    # ==================== 添加成员相关方法 ====================

    @allure.step("点击账号管理链接")
    def click_account_management(self):
        self.account_management_link.wait_for(state="visible")
        self.account_management_link.click()

    @allure.step("点击添加成员按钮")
    def click_add_member(self):
        self.add_member_button.wait_for(state="visible")
        self.add_member_button.click()

    @allure.step("输入手机号搜索：{phone}")
    def input_phone_search(self, phone: str):
        self.member_phone_search_input.wait_for(state="visible")
        self.member_phone_search_input.clear()
        self.member_phone_search_input.fill(phone)

    @allure.step("勾选成员复选框")
    def check_member(self):
        self.member_checkbox.wait_for(state="visible")
        if not self.member_checkbox.is_checked():
            self.member_checkbox.check()

    def has_selectable_member(self) -> bool:
        return self.page.locator(".ant-modal-body .ant-checkbox-input").count() > 0

    @allure.step("点击确定按钮")
    def click_confirm(self):
        self.confirm_button.wait_for(state="visible")
        self.confirm_button.click()

    @allure.step("执行添加成员操作")
    def add_member(self, phone: str = "") -> bool:
        self.click_account_management()
        self.click_add_member()
        if phone:
            self.input_phone_search(phone)
            self.page.wait_for_timeout(800)

        if not self.has_selectable_member():
            self.member_phone_search_input.clear()
            self.page.wait_for_timeout(800)

        if not self.has_selectable_member():
            return False

        self.check_member()
        self.click_confirm()
        return True
