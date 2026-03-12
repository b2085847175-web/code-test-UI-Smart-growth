"""
登录功能测试用例
网站：https://dev.aigrowth8.com/login
"""
import pytest
import allure
import re
from playwright.sync_api import expect
from pages.login_page import LoginPage


@allure.epic("用户管理模块")
@allure.feature("登录功能")
class TestLogin:
    """登录功能测试类"""

    @allure.story("正常登录")
    @allure.title("使用正确的手机号码和密码登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.login
    def test_login_success(self, page, env_config):
        """
        测试用例：使用正确的手机号码和密码登录成功

        前置条件：
            - 访问登录页面

        测试步骤：
            1. 输入正确的手机号码
            2. 输入正确的密码
            3. 点击登录按钮

        预期结果：
            - 登录成功，URL 离开登录页
        """
        login_page = LoginPage(page)

        with allure.step("步骤1：导航到登录页面"):
            login_page.navigate(env_config["base_url"])

        with allure.step("步骤2：验证登录页面加载完成"):
            expect(login_page.phone_input).to_be_visible()
            expect(login_page.password_input).to_be_visible()
            expect(login_page.login_button).to_be_visible()

        with allure.step("步骤3：执行登录操作"):
            login_page.login(env_config["username"], env_config["password"])

        with allure.step("验证：登录成功，URL 离开登录页"):
            expect(page).not_to_have_url(re.compile(r".*/login.*"), timeout=10000)

    @allure.story("异常登录")
    @allure.title("使用错误的密码登录")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.login
    def test_login_wrong_password(self, page, env_config):
        """
        测试用例：使用错误的密码登录

        前置条件：
            - 访问登录页面

        测试步骤：
            1. 输入正确的手机号码
            2. 输入错误的密码
            3. 点击登录按钮

        预期结果：
            - 登录失败，显示错误信息
        """
        login_page = LoginPage(page)

        with allure.step("步骤1：导航到登录页面"):
            login_page.navigate(env_config["base_url"])

        with allure.step("步骤2：验证登录页面加载完成"):
            expect(login_page.phone_input).to_be_visible()
            expect(login_page.password_input).to_be_visible()
            expect(login_page.login_button).to_be_visible()

        with allure.step("步骤3：输入手机号码和错误的密码"):
            login_page.input_phone(env_config["username"])
            login_page.input_password("wrong_password_123")

        with allure.step("步骤4：点击登录按钮"):
            login_page.click_login_button()

        with allure.step("验证：显示错误提示信息"):
            expect(login_page.error_message).to_be_visible(timeout=5000)

    @allure.story("异常登录")
    @allure.title("手机号码为空时登录")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.login
    def test_login_empty_phone(self, page, env_config):
        """
        测试用例：手机号码为空时登录

        前置条件：
            - 访问登录页面

        测试步骤：
            1. 手机号码留空
            2. 输入密码
            3. 点击登录按钮

        预期结果：
            - 登录失败，显示错误信息
        """
        login_page = LoginPage(page)

        with allure.step("步骤1：导航到登录页面"):
            login_page.navigate(env_config["base_url"])

        with allure.step("步骤2：验证登录页面加载完成"):
            expect(login_page.phone_input).to_be_visible()
            expect(login_page.password_input).to_be_visible()
            expect(login_page.login_button).to_be_visible()

        with allure.step("步骤3：手机号码为空，输入密码"):
            login_page.input_phone("")
            login_page.input_password(env_config["password"])

        with allure.step("步骤4：点击登录按钮"):
            login_page.click_login_button()

        with allure.step("验证：显示错误提示信息"):
            expect(login_page.error_message).to_be_visible(timeout=5000)

    @allure.story("异常登录")
    @allure.title("密码为空时登录")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.login
    def test_login_empty_password(self, page, env_config):
        """
        测试用例：密码为空时登录

        前置条件：
            - 访问登录页面

        测试步骤：
            1. 输入手机号码
            2. 密码留空
            3. 点击登录按钮

        预期结果：
            - 登录失败，显示错误信息
        """
        login_page = LoginPage(page)

        with allure.step("步骤1：导航到登录页面"):
            login_page.navigate(env_config["base_url"])

        with allure.step("步骤2：验证登录页面加载完成"):
            expect(login_page.phone_input).to_be_visible()
            expect(login_page.password_input).to_be_visible()
            expect(login_page.login_button).to_be_visible()

        with allure.step("步骤3：输入手机号码，密码为空"):
            login_page.input_phone(env_config["username"])
            login_page.input_password("")

        with allure.step("步骤4：点击登录按钮"):
            login_page.click_login_button()

        with allure.step("验证：显示错误提示信息"):
            expect(login_page.error_message).to_be_visible(timeout=5000)
