"""
Pytest 配置文件
包含全局 fixture 和钩子函数
"""
import re
import traceback

import pytest
from playwright.sync_api import sync_playwright, expect
from utils.helpers import config_loader
import allure


@pytest.fixture(scope="session")
def playwright():
    """
    Playwright 实例 fixture
    作用域：整个测试会话
    """
    with sync_playwright() as p:
        yield p


def pytest_addoption(parser):
    """
    添加自定义命令行参数
    """
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="运行环境: dev/test/prod"
    )
    parser.addoption(
        "--headless",
        action="store",
        default=None,
        help="覆盖配置中的浏览器无头模式: true/false"
    )


@pytest.fixture(scope="function")
def browser(playwright, request):
    """
    浏览器 fixture
    作用域：每个测试函数
    支持从 config 读取 headless、slow_mo 配置
    """
    browser_config = config_loader.get_browser_config()
    browser_type = browser_config["type"]
    headless_option = request.config.getoption("--headless")
    if headless_option is None:
        headless = browser_config["headless"]
    else:
        headless = str(headless_option).strip().lower() == "true"
    slow_mo = browser_config["slow_mo"]

    # 启动浏览器
    if browser_type == "chromium":
        browser = playwright.chromium.launch(
            headless=headless,
            slow_mo=slow_mo
        )
    elif browser_type == "firefox":
        browser = playwright.firefox.launch(
            headless=headless,
            slow_mo=slow_mo
        )
    elif browser_type == "webkit":
        browser = playwright.webkit.launch(
            headless=headless,
            slow_mo=slow_mo
        )
    else:
        raise ValueError(f"不支持的浏览器类型: {browser_type}")

    yield browser

    # 测试结束后关闭浏览器
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    """
    浏览器上下文 fixture
    作用域：每个测试函数
    每个测试函数都有独立的上下文，避免测试之间的影响
    """
    browser_config = config_loader.get_browser_config()
    viewport = browser_config["viewport"]

    # 创建新的浏览器上下文
    context = browser.new_context(
        viewport=viewport,
        ignore_https_errors=browser_config.get("ignore_https_errors", False)
    )

    yield context

    # 测试结束后关闭上下文
    context.close()


@pytest.fixture(scope="function")
def page(context):
    """
    页面 fixture
    作用域：每个测试函数
    提供 Playwright Page 对象
    """
    # 创建新页面
    page = context.new_page()

    # 设置默认超时时间
    browser_config = config_loader.get_browser_config()
    page.set_default_timeout(browser_config["timeout"])

    yield page

    # 测试结束后关闭页面
    page.close()


@pytest.fixture(scope="session")
def env_config(request):
    """
    环境配置 fixture
    作用域：整个测试会话
    """
    env = request.config.getoption("--env")
    return config_loader.get_env_config(env)


@pytest.fixture(scope="function")
def logged_in_page(page, env_config):
    """
    已登录页面 fixture
    作用域：每个测试函数
    """
    from pages.login_page import LoginPage

    login_page = LoginPage(page)
    login_page.navigate(env_config["base_url"])
    login_page.login(env_config["username"], env_config["password"])
    expect(page).not_to_have_url(re.compile(r".*/login.*"), timeout=15000)
    return page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest 钩子函数
    用于在测试失败时自动截图
    """
    outcome = yield
    rep = outcome.get_result()

    # 只在测试调用阶段执行
    if rep.when == "call" and rep.failed:
        # 尝试获取 page fixture
        try:
            page = item.funcargs["page"]
            # 截图并附加到 Allure 报告
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name="失败截图",
                attachment_type=allure.attachment_type.PNG
            )
        except Exception:
            allure.attach(
                traceback.format_exc(),
                name="截图失败堆栈",
                attachment_type=allure.attachment_type.TEXT
            )
