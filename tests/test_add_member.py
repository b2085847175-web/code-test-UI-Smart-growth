"""
添加成员功能测试用例
网站：https://dev.aigrowth8.com
"""
import pytest
import allure
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.member_management_page import MemberManagementPage


@allure.epic("用户管理模块")
@allure.feature("添加成员功能")
class TestAddMember:
    """添加成员功能测试类"""

    @allure.story("正常添加成员")
    @allure.title("成功添加成员")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_add_member_success(self, page, env_config):
        """
        测试用例：成功添加成员

        前置条件：
            - 已登录系统

        测试步骤：
            1. 点击账号管理
            2. 点击添加成员
            3. 输入手机号搜索
            4. 勾选成员
            5. 点击确定

        预期结果：
            - 显示成功提示："成功添加 1 名成员"
        """
        login_page = LoginPage(page)
        member_page = MemberManagementPage(page)

        with allure.step("步骤1：导航到登录页面并登录"):
            login_page.navigate(env_config["base_url"])
            login_page.login(env_config["username"], env_config["password"])

        with allure.step("步骤2：等待登录成功，URL 离开登录页"):
            expect(page).not_to_have_url("/login", timeout=15000)

        with allure.step("步骤3：执行添加成员操作"):
            member_page.add_member("13000000000")

        with allure.step("验证：显示成功提示信息"):
            expect(member_page.success_message).to_be_visible(timeout=5000)
