"""
账号管理操作流测试（先覆盖操作，不做业务断言）
"""
import pytest
import allure
from pages.account_management_page import AccountManagementPage
from data.account_data import build_account_create_data


@allure.epic("用户管理模块")
@allure.feature("账号管理操作")
class TestAccountManagementOperations:
    """账号管理操作测试类"""

    @allure.story("新增账号与搜索操作")
    @allure.title("登录后进入账号管理，新增账号并操作两个搜索输入框")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_account_and_search_inputs(self, logged_in_page):
        """
        测试步骤：
            1. 进入账号管理
            2. 点击新增账号
            3. 填写账号信息并保存
            4. 操作手机号搜索输入框
            5. 操作姓名搜索输入框
        """
        account_page = AccountManagementPage(logged_in_page)
        account_data = build_account_create_data()

        with allure.step("步骤1-3：新增账号"):
            account_page.create_account(**account_data)

        with allure.step("步骤4：操作手机号搜索输入框"):
            account_page.click_list_phone_search_input()
            account_page.input_list_phone_search(account_data["phone"])

        with allure.step("步骤5：操作姓名搜索输入框"):
            account_page.click_list_name_search_input()
            account_page.input_list_name_search(account_data["name"])
