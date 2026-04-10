"""
团队场景下的工单页面。

覆盖从首页进入团队工单列表，并将已流转工单继续分配给个人的流程。
"""
import re
import time
from datetime import datetime, timedelta
from typing import Optional

import allure
from playwright.sync_api import Locator
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect


class TeamWorkOrderPage:
    """
    团队工单页面对象。
    """

    def __init__(self, page: Page):
        self.page = page

    # ==================== 通用辅助 ====================

    def _wait_optional_hidden(
        self,
        locator: Locator,
        timeout: int = 10000
    ) -> None:
        try:
            locator.first.wait_for(state="hidden", timeout=timeout)
        except PlaywrightTimeoutError:
            pass

    def wait_for_ui_stable(self, timeout: int = 10000) -> None:
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except PlaywrightTimeoutError:
            pass

        try:
            self.page.wait_for_load_state("networkidle", timeout=2000)
        except PlaywrightTimeoutError:
            pass

        self._wait_optional_hidden(
            self.page.locator(".ant-spin-spinning"),
            timeout=timeout
        )

    def _click_and_wait(
        self,
        locator: Locator,
        timeout: int = 10000
    ) -> None:
        locator.wait_for(state="visible", timeout=timeout)
        locator.click()
        self.wait_for_ui_stable(timeout=timeout)

    def _click_first_visible(
        self,
        locator: Locator,
        timeout: int = 10000
    ) -> None:
        end_time = time.time() + timeout / 1000
        last_error: Optional[Exception] = None

        while time.time() < end_time:
            count = locator.count()
            for index in range(count):
                candidate = locator.nth(index)
                try:
                    if candidate.is_visible():
                        candidate.scroll_into_view_if_needed(timeout=1000)
                        candidate.click()
                        self.wait_for_ui_stable(timeout=timeout)
                        return
                except Exception as exc:  # pragma: no cover - UI fallback
                    last_error = exc

            self.page.wait_for_timeout(200)

        if last_error is not None:
            raise last_error

        locator.first.wait_for(state="visible", timeout=timeout)
        locator.first.click()
        self.wait_for_ui_stable(timeout=timeout)

    def _fill_input(
        self,
        locator: Locator,
        value: str,
        timeout: int = 10000
    ) -> None:
        locator.wait_for(state="visible", timeout=timeout)
        locator.click()
        locator.clear()
        locator.fill(value)

    def _is_visible(self, locator: Locator, timeout: int = 2000) -> bool:
        try:
            locator.first.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def _is_team_work_order_page_ready(self, timeout: int = 5000) -> bool:
        # 团队工单页应存在搜索框，且不应出现“新建工单”按钮。
        return (
            self._is_visible(self.work_order_search_input, timeout=timeout)
            and not self._is_visible(self.new_work_order_button, timeout=2000)
        )

    def _get_visible_dropdown(self) -> Locator:
        return self.page.locator(
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden)"
        ).last

    def _get_visible_picker(self) -> Locator:
        return self.page.locator(".ant-picker-dropdown:visible").last

    def _select_dropdown_option(
        self,
        trigger: Locator,
        option_text: str,
        timeout: int = 10000
    ) -> None:
        trigger.wait_for(state="visible", timeout=timeout)
        trigger.click()

        dropdown = self._get_visible_dropdown()
        dropdown.wait_for(state="visible", timeout=timeout)

        option = dropdown.get_by_title(option_text).first
        try:
            option.wait_for(state="visible", timeout=3000)
        except PlaywrightTimeoutError:
            option = dropdown.get_by_text(option_text, exact=True).first
            option.wait_for(state="visible", timeout=timeout)

        option.click()
        self.wait_for_ui_stable(timeout=timeout)

    def _select_time_cell(
        self,
        column: Locator,
        value: int,
        timeout: int = 10000
    ) -> None:
        texts = (f"{value:02d}", str(value))
        last_error: Optional[Exception] = None

        for text in texts:
            candidate = column.get_by_text(text, exact=True).first
            try:
                candidate.wait_for(state="visible", timeout=1500)
                candidate.click()
                return
            except Exception as exc:  # pragma: no cover - UI fallback
                last_error = exc

        if last_error is not None:
            raise last_error

    # ==================== 页面元素 ====================

    @property
    def work_order_search_input(self) -> Locator:
        return self.page.get_by_placeholder("请输入工单号、工单标题、商品ID")

    @property
    def work_order_list_rows(self) -> Locator:
        return self.page.locator(
            ".ant-table-tbody tr:not(.ant-table-measure-row)"
        )

    @property
    def new_work_order_button(self) -> Locator:
        return self.page.get_by_role(
            "button",
            name=re.compile(r"(plus\s*)?新建工单")
        )

    @property
    def detail_panel(self) -> Locator:
        return self.page.locator(
            ".ant-drawer-content:visible, .ant-modal-content:visible"
        ).last

    @property
    def detail_transfer_button(self) -> Locator:
        return self.detail_panel.get_by_role(
            "button",
            name=re.compile(r"流\s*转")
        ).first

    @property
    def assignee_selector(self) -> Locator:
        return self.page.get_by_label("分配人员")

    @property
    def transfer_drawer(self) -> Locator:
        return self.page.locator(
            ".ant-drawer-content:visible, .ant-modal-content:visible"
        ).last

    @property
    def transfer_dialog(self) -> Locator:
        # 以“分配人员”字段反向定位当前流转弹窗，避免误取详情面板。
        return self.assignee_selector.locator(
            "xpath=ancestor::*[contains(@class, 'ant-drawer-content') or "
            "contains(@class, 'ant-modal-content')]"
        ).first

    @property
    def view_buttons(self) -> Locator:
        return self.page.get_by_role(
            "button",
            name=re.compile(r"(eye\s*)?查看")
        )

    @property
    def appointment_validation_message(self) -> Locator:
        return self.page.get_by_text("第1个预约时间必须是未来的时间")

    # ==================== 业务动作 ====================

    def team_entry_candidates(self, team_name: str) -> Locator:
        # 组织/团队选择页存在同名文本，优先限定在卡片入口内，规避右上角用户信息误匹配。
        card_entries = self.page.locator(".ant-card").filter(
            has=self.page.locator(".cardTitle").filter(
                has_text=re.compile(rf"^{re.escape(team_name)}$")
            )
        )
        if card_entries.count() > 0:
            return card_entries

        # 兜底：若卡片结构变更，至少保留精确文本定位。
        return self.page.get_by_text(team_name, exact=True)

    def work_order_row(self, keyword: str) -> Locator:
        return self.work_order_list_rows.filter(has_text=keyword).first

    def specification_appointment_input(self, index: int) -> Locator:
        placeholder = self.page.locator(
            "[placeholder='请选择预约时间']:visible"
        ).nth(index)
        return placeholder.locator(
            "xpath=ancestor::*[contains(@class, 'ant-picker')]"
        ).first

    @allure.step("从首页进入团队工单页：{team_name}")
    def navigate_to_team_work_orders(
        self,
        base_url: str,
        team_name: str,
        timeout: int = 15000
    ) -> None:
        self.page.goto(base_url)
        self.wait_for_ui_stable(timeout=timeout)

        candidates = self.team_entry_candidates(team_name)
        count = candidates.count()
        if count == 0:
            raise AssertionError(f"未找到团队入口：{team_name}")
        # 多个候选时优先最后一个，兼容页面把团队入口排在组织入口后面的常见布局。
        target = candidates.last if count > 1 else candidates.first
        target.scroll_into_view_if_needed(timeout=1000)
        target.click()
        self.wait_for_ui_stable(timeout=timeout)

        if not self._is_team_work_order_page_ready(timeout=timeout):
            raise AssertionError(
                f"点击后未进入团队工单页，可能误入同名组织入口：{team_name}"
            )

    @allure.step("按关键字搜索团队工单：{keyword}")
    def search_work_order(self, keyword: str) -> None:
        self._fill_input(self.work_order_search_input, keyword, timeout=15000)
        self.work_order_search_input.press("Enter")
        self.wait_for_ui_stable(timeout=15000)
        self.page.wait_for_timeout(800)

    @allure.step("打开目标团队工单详情：{keyword}")
    def open_work_order_detail(
        self,
        keyword: str,
        timeout: int = 15000
    ) -> None:
        target_row = self.work_order_row(keyword)
        target_row.wait_for(state="visible", timeout=timeout)

        action_button = target_row.get_by_role("button").first
        action_button.wait_for(state="visible", timeout=timeout)
        action_button.click()
        self.wait_for_ui_stable(timeout=timeout)
        self.detail_panel.wait_for(state="visible", timeout=timeout)
        self.page.wait_for_timeout(1000)

    @allure.step("点击团队详情中的流转按钮")
    def click_detail_transfer_button(self, timeout: int = 15000) -> None:
        self._click_and_wait(self.detail_transfer_button, timeout=timeout)
        self.page.wait_for_timeout(1000)

    @allure.step("等待工单流转弹窗")
    def wait_for_transfer_dialog(self, timeout: int = 15000) -> None:
        self.transfer_dialog.wait_for(state="visible", timeout=timeout)
        self.assignee_selector.wait_for(state="visible", timeout=timeout)
        self.page.wait_for_timeout(1000)

    @allure.step("提交流转到个人")
    def submit_transfer_to_member(self, timeout: int = 15000) -> None:
        dialog = self.transfer_dialog
        dialog.wait_for(state="visible", timeout=timeout)

        submit_button = dialog.get_by_role(
            "button",
            name=re.compile(r"流\s*转|确\s*定|提\s*交")
        ).last
        try:
            submit_button.wait_for(state="visible", timeout=3000)
        except PlaywrightTimeoutError:
            submit_button = dialog.locator("button.ant-btn-primary").last
            submit_button.wait_for(state="visible", timeout=timeout)

        submit_button.click(force=True)
        self.wait_for_ui_stable(timeout=timeout)

        # 最终提交后，流转弹窗必须消失，否则视为提交未成功。
        dialog.wait_for(state="hidden", timeout=timeout)

    @allure.step("处理预约时间校验提示")
    def dismiss_appointment_validation_if_present(self) -> None:
        if self._is_visible(self.appointment_validation_message, timeout=3000):
            self.appointment_validation_message.first.click()
            self.wait_for_ui_stable(timeout=5000)

    @allure.step("设置第 {index} 行预约时间")
    def set_future_appointment_time(
        self,
        index: int,
        offset_minutes: int,
        timeout: int = 15000
    ) -> None:
        target_time = datetime.now() + timedelta(minutes=offset_minutes)
        target_value = target_time.strftime("%Y-%m-%d %H:%M")
        appointment_input = self.specification_appointment_input(index)
        appointment_input.wait_for(state="visible", timeout=timeout)
        text_input = appointment_input.locator("input").first
        text_input.wait_for(state="visible", timeout=timeout)

        try:
            text_input.click(force=True)
            text_input.fill(target_value)
            text_input.press("Enter")
            self.wait_for_ui_stable(timeout=timeout)
            self.page.wait_for_timeout(1000)
            return
        except Exception:  # pragma: no cover - UI fallback
            pass

        appointment_input.scroll_into_view_if_needed(timeout=1000)
        appointment_input.click(force=True)

        picker = self._get_visible_picker()
        picker.wait_for(state="visible", timeout=timeout)

        now_button = picker.get_by_text("此刻", exact=True).first
        if self._is_visible(now_button, timeout=2000):
            now_button.click()
            self.wait_for_ui_stable(timeout=timeout)
            appointment_input.scroll_into_view_if_needed(timeout=1000)
            appointment_input.click(force=True)
            picker = self._get_visible_picker()
            picker.wait_for(state="visible", timeout=timeout)

        columns = picker.locator(".ant-picker-time-panel-column")
        column_count = columns.count()

        if column_count >= 1:
            self._select_time_cell(columns.nth(0), target_time.hour, timeout=timeout)
        if column_count >= 2:
            self._select_time_cell(
                columns.nth(1),
                target_time.minute,
                timeout=timeout
            )
        if column_count >= 3:
            self._select_time_cell(
                columns.nth(2),
                target_time.second,
                timeout=timeout
            )

        confirm_button = picker.locator("button.ant-btn-primary").last
        confirm_button.wait_for(state="visible", timeout=timeout)
        confirm_button.click(force=True)
        self.wait_for_ui_stable(timeout=timeout)
        self.page.wait_for_timeout(1000)

    @allure.step("补齐所有规格的预约时间")
    def set_future_appointment_times_for_all_specifications(
        self,
        specification_count: int
    ) -> None:
        # 团队流转到个人前，先把所有规格的预约时间统一补成“当前时间 + 2 分钟”。
        for index in range(specification_count):
            self.set_future_appointment_time(
                index=index,
                offset_minutes=2
            )
        self.page.wait_for_timeout(1000)

    @allure.step("选择分配人员：{assignee_display_name}")
    def select_assignee(
        self,
        assignee_display_name: str,
        timeout: int = 15000
    ) -> None:
        self._select_dropdown_option(
            self.assignee_selector,
            assignee_display_name,
            timeout=timeout
        )
        self.page.wait_for_timeout(1000)

    @allure.step("将团队工单分配给个人")
    def assign_work_order_to_member(
        self,
        base_url: str,
        team_name: str,
        keyword: str,
        assignee_display_name: str,
        specification_count: int
    ) -> None:
        # 1. 回到首页后进入团队工单页，并按关键字找到刚流转过来的工单。
        self.navigate_to_team_work_orders(base_url=base_url, team_name=team_name)
        self.search_work_order(keyword)
        self.open_work_order_detail(keyword)

        # 2. 先补齐预约时间，再打开“工单流转”弹窗，避免直接流转时触发时间校验。
        self.set_future_appointment_times_for_all_specifications(
            specification_count=specification_count
        )
        self.click_detail_transfer_button()
        self.dismiss_appointment_validation_if_present()

        if not self._is_visible(self.assignee_selector, timeout=3000):
            # 3. 如果第一次没有成功打开分配弹窗，则补一次时间并重新尝试打开。
            self.set_future_appointment_times_for_all_specifications(
                specification_count=specification_count
            )
            self.click_detail_transfer_button()

        # 4. 选择分配人员，并点击最终“流转”按钮提交到个人。
        self.wait_for_transfer_dialog()
        self.select_assignee(assignee_display_name)
        self.submit_transfer_to_member()

        # 5. 以页面仍可见“查看”按钮作为提交后的基本稳定标志。
        expect(self.view_buttons.first).to_be_visible(timeout=15000)
