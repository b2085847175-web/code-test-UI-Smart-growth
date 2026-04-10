"""
Pytest 配置文件
包含全局 fixture 和钩子函数
"""
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable

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


def _sanitize_nodeid(nodeid: str) -> str:
    sanitized = re.sub(r"[^0-9A-Za-z._-]+", "_", nodeid).strip("._-")
    return sanitized or "test_case"


def _build_case_log_dir(nodeid: str) -> Path:
    project_root = Path(__file__).resolve().parent
    logs_root = project_root / "logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    case_dir = logs_root / f"{timestamp}_{_sanitize_nodeid(nodeid)}"
    case_dir.mkdir(parents=True, exist_ok=True)
    return case_dir


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
def context(browser, request):
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

    case_log_dir = _build_case_log_dir(request.node.nodeid)
    action_log_path = case_log_dir / "browser_actions.log"
    trace_zip_path = case_log_dir / "trace.zip"

    action_log_file = open(
        action_log_path,
        mode="a",
        encoding="utf-8",
        buffering=1
    )

    def log_action(message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        action_log_file.write(f"{timestamp} {message}\n")

    log_action(f"[CASE_START] nodeid={request.node.nodeid}")
    log_action(f"[LOG_PATH] action_log={action_log_path}")
    log_action(f"[TRACE_PATH] trace_zip={trace_zip_path}")

    attached_page_ids = set()

    def attach_page_logging(page) -> None:
        page_id = id(page)
        if page_id in attached_page_ids:
            return
        attached_page_ids.add(page_id)

        log_action(f"[PAGE_OPEN] page_id={page_id} url={page.url}")

        def on_frame_navigated(frame) -> None:
            if frame == page.main_frame:
                log_action(
                    f"[NAVIGATE] page_id={page_id} url={frame.url}"
                )

        def on_request(req) -> None:
            log_action(
                f"[REQUEST] page_id={page_id} method={req.method} "
                f"type={req.resource_type} url={req.url}"
            )

        def on_response(resp) -> None:
            status_tag = "RESPONSE_ERR" if resp.status >= 400 else "RESPONSE"
            log_action(
                f"[{status_tag}] page_id={page_id} status={resp.status} "
                f"method={resp.request.method} url={resp.url}"
            )

        def on_request_failed(req) -> None:
            failure = req.failure
            failure_text = (
                failure.get("errorText", "")
                if isinstance(failure, dict)
                else str(failure)
            )
            log_action(
                f"[REQUEST_FAILED] page_id={page_id} method={req.method} "
                f"url={req.url} error={failure_text}"
            )

        def on_console(msg) -> None:
            text = msg.text.replace("\n", "\\n")
            log_action(
                f"[CONSOLE] page_id={page_id} type={msg.type} text={text}"
            )

        def on_page_error(error) -> None:
            log_action(
                f"[PAGE_ERROR] page_id={page_id} error={error}"
            )

        def on_dialog(dialog) -> None:
            dialog_message = dialog.message.replace("\n", "\\n")
            log_action(
                f"[DIALOG] page_id={page_id} type={dialog.type} "
                f"message={dialog_message}"
            )

        def on_close() -> None:
            log_action(f"[PAGE_CLOSE] page_id={page_id}")

        page.on("framenavigated", on_frame_navigated)
        page.on("request", on_request)
        page.on("response", on_response)
        page.on("requestfailed", on_request_failed)
        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("dialog", on_dialog)
        page.on("close", on_close)

    context._log_action = log_action
    context._attach_page_logging = attach_page_logging
    context._case_log_dir = case_log_dir

    context.on("page", attach_page_logging)

    trace_started = False
    try:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        trace_started = True
        log_action("[TRACE_START] tracing started")
    except Exception as exc:
        log_action(f"[TRACE_START_ERROR] {exc}")

    yield context

    if trace_started:
        try:
            context.tracing.stop(path=str(trace_zip_path))
            log_action(f"[TRACE_SAVED] {trace_zip_path}")
        except Exception as exc:
            log_action(f"[TRACE_STOP_ERROR] {exc}")

    log_action("[CASE_END] teardown context")
    action_log_file.close()

    # 测试结束后关闭上下文
    context.close()

    print(f"[browser-log] {action_log_path}")
    print(f"[browser-trace] {trace_zip_path}")


@pytest.fixture(scope="function")
def page(context):
    """
    页面 fixture
    作用域：每个测试函数
    提供 Playwright Page 对象
    """
    # 创建新页面
    page = context.new_page()
    attach_page_logging: Callable | None = getattr(
        context,
        "_attach_page_logging",
        None
    )
    if callable(attach_page_logging):
        attach_page_logging(page)

    # 设置默认超时时间
    browser_config = config_loader.get_browser_config()
    page.set_default_timeout(browser_config["timeout"])
    log_action: Callable | None = getattr(context, "_log_action", None)
    if callable(log_action):
        log_action(
            f"[PAGE_TIMEOUT] page_id={id(page)} timeout={browser_config['timeout']}"
        )

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
