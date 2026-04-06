"""
组织场景下的我的工单页面。

覆盖从组织首页进入“我的工单”并创建工单的主流程操作。
"""
import re
import time
from typing import Optional

import allure
from playwright.sync_api import Locator
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from data.work_order_data import (
    OrganizationWorkOrderCreateData,
    WorkOrderSpecificationData,
)

class OrganizationWorkOrderPage:
    """
    组织下“我的工单”页面对象。
    """

    def __init__(self, page: Page):
        self.page = page

    # ==================== 通用辅助 ====================

    def _wait_optional_hidden(
        self,
        locator: Locator,
        timeout: int = 10000
    ) -> None:
        """
        等待可选的加载元素消失；不存在时直接跳过。
        """
        try:
            locator.first.wait_for(state="hidden", timeout=timeout)
        except PlaywrightTimeoutError:
            pass

    def wait_for_ui_stable(self, timeout: int = 10000) -> None:
        # 先等页面和加载状态稳定，再执行下一步。
        """
        等待页面进入相对稳定状态。

        由于系统偶发卡顿，关键动作后统一等待可降低误触发概率。
        """
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
        # 有多个同名元素时，优先点击当前可见的那个。
        """
        针对录制类页面上可能出现的多个同名元素，点击第一个可见元素。
        """
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
                except Exception as exc:  # pragma: no cover - fallback branch
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

    def _get_visible_dropdown(self) -> Locator:
        return self.page.locator(
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden)"
        ).last

    def _select_dropdown_option(
        self,
        trigger: Locator,
        option_text: str,
        timeout: int = 10000
    ) -> None:
        # 统一处理下拉框的展开、选择和等待。
        trigger.wait_for(state="visible", timeout=timeout)
        trigger.click()

        dropdown = self._get_visible_dropdown()
        dropdown.wait_for(state="visible", timeout=timeout)

        option = dropdown.get_by_title(option_text).first
        try:
            option.wait_for(state="visible", timeout=1500)
            option.click()
        except PlaywrightTimeoutError:
            dropdown.get_by_text(option_text, exact=True).last.click()

        self.wait_for_ui_stable(timeout=timeout)

    def _set_rich_text(
        self,
        value: str,
        timeout: int = 10000
    ) -> None:
        candidates = (
            self.work_order_form.locator("[contenteditable='true']").first,
            self.work_order_form.locator("pre").first,
        )

        last_error: Optional[Exception] = None
        for locator in candidates:
            try:
                locator.wait_for(state="visible", timeout=2000)
                locator.click()
                locator.fill(value)
                return
            except Exception as exc:  # pragma: no cover - fallback branch
                last_error = exc

        if last_error is not None:
            raise last_error

    # ==================== 页面元素 ====================

    @property
    def my_work_orders_link(self) -> Locator:
        return self.page.get_by_role("link", name="我的工单")

    @property
    def new_work_order_button(self) -> Locator:
        return self.page.get_by_role(
            "button",
            name=re.compile(r"(plus\s*)?新建工单")
        )

    @property
    def work_order_form(self) -> Locator:
        return self.page.locator("#work-order-form")

    @property
    def work_order_type_layer(self) -> Locator:
        return self.page.locator(
            ".ant-drawer-content:visible, .ant-modal-content:visible"
        ).last

    @property
    def proxy_creator_selector(self) -> Locator:
        return self.work_order_form.locator("div").filter(
            has_text=re.compile(r"^请输入姓名搜索代为创建人$")
        ).first

    @property
    def ecommerce_platform_selector(self) -> Locator:
        return self.work_order_form.get_by_role(
            "combobox",
            name=re.compile(r"^\*?\s*电商平台$")
        )

    @property
    def store_selector(self) -> Locator:
        return self.work_order_form.get_by_role(
            "combobox",
            name=re.compile(r"^\*?\s*店铺$")
        )

    @property
    def product_id_input(self) -> Locator:
        return self.work_order_form.get_by_role(
            "textbox",
            name=re.compile(r"^\*?\s*商品ID$")
        )

    @property
    def product_link_input(self) -> Locator:
        return self.work_order_form.get_by_role(
            "textbox",
            name=re.compile(r"^\*?\s*商品链接$")
        )

    @property
    def product_title_input(self) -> Locator:
        return self.work_order_form.get_by_role(
            "textbox",
            name=re.compile(r"^\*?\s*商品标题$")
        )

    @property
    def product_name_input(self) -> Locator:
        return self.work_order_form.get_by_role(
            "textbox",
            name=re.compile(r"^\*?\s*商品名称$")
        )

    @property
    def delivery_code_input(self) -> Locator:
        return self.work_order_form.get_by_role(
            "textbox",
            name=re.compile(r"^\*?\s*发货编码$")
        )

    @property
    def group_maintenance_selector(self) -> Locator:
        return self.work_order_form.get_by_role(
            "combobox",
            name=re.compile(r"^\*?\s*开群维护$")
        )

    @property
    def completion_days_input(self) -> Locator:
        return self.work_order_form.get_by_role(
            "textbox",
            name=re.compile(r"^\*?\s*完成天数$")
        )

    @property
    def review_required_selector(self) -> Locator:
        return self.work_order_form.get_by_role(
            "combobox",
            name=re.compile(r"^\*?\s*是否评价$")
        )

    @property
    def file_input(self) -> Locator:
        return self.work_order_form.locator("input[type='file']").first

    @property
    def preview_image_link(self) -> Locator:
        return self.work_order_form.get_by_role("link", name="eye").first

    @property
    def add_specification_button(self) -> Locator:
        return self.page.get_by_role(
            "button",
            name=re.compile(r"(plus\s*)?添加规格")
        )

    @property
    def specification_rows(self) -> Locator:
        return self.page.locator(
            ".ant-table-tbody tr:not(.ant-table-measure-row)"
        )

    @property
    def save_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"保\s*存"))

    @property
    def confirm_buttons(self) -> Locator:
        return self.page.get_by_role("button", name="确 定")

    @property
    def confirm_button(self) -> Locator:
        return self.confirm_buttons.last

    @property
    def visible_confirm_buttons(self) -> Locator:
        return self.page.locator("button:visible").filter(
            has_text=re.compile(r"^\s*确\s*定\s*$")
        )

    @property
    def image_preview_close_button(self) -> Locator:
        return self.page.locator(".ant-image-preview-close, .ant-modal-close").first

    # ==================== 业务动作 ====================

    def organization_entry(self, organization_name: str) -> Locator:
        return self.page.get_by_text(organization_name, exact=True).first

    def work_order_type_option(self, work_order_type: str) -> Locator:
        return self.work_order_type_layer.get_by_text(
            work_order_type,
            exact=True
        )

    def specification_row(self, index: int) -> Locator:
        return self.specification_rows.nth(index)

    def specification_name_input(self, index: int) -> Locator:
        return self.work_order_form.get_by_placeholder("输入规格").nth(index)

    def specification_quantity_input(self, index: int) -> Locator:
        return self.work_order_form.get_by_placeholder("请输入单数").nth(index)

    def specification_price_input(self, index: int) -> Locator:
        return self.work_order_form.get_by_placeholder("请输入价格").nth(index)

    def specification_appointment_input(self, index: int) -> Locator:
        return self.work_order_form.get_by_placeholder("请选择预约时间").nth(index)

    def navigate_to_my_work_orders(self, organization_name: str) -> None:
        """
        从组织入口进入“我的工单”页面。
        """
        self._click_and_wait(self.organization_entry(organization_name))
        self._click_and_wait(self.my_work_orders_link)
        expect(self.new_work_order_button).to_be_visible(timeout=10000)

    @allure.step("点击新建工单按钮")
    def click_new_work_order(self, work_order_type: Optional[str] = None) -> None:
        self._click_and_wait(self.new_work_order_button)
        # 点击新建后会先出现工单类型，选中后才会进入表单。
        if work_order_type:
            expect(self.work_order_type_option(work_order_type).first).to_be_visible(
                timeout=15000
            )
        else:
            expect(self.work_order_type_layer).to_be_visible(timeout=15000)

    @allure.step("选择工单类型：{work_order_type}")
    def select_work_order_type(self, work_order_type: str) -> None:
        self._click_first_visible(
            self.work_order_type_option(work_order_type),
            timeout=15000
        )
        # 选完工单类型后，等待工单表单真正出现。
        self.work_order_form.wait_for(state="visible", timeout=15000)

    @allure.step("选择代为创建人：{creator_name}")
    def select_proxy_creator(self, creator_name: str) -> None:
        self.proxy_creator_selector.wait_for(state="visible", timeout=10000)
        self.proxy_creator_selector.click()
        self.page.get_by_title(creator_name).first.wait_for(
            state="visible",
            timeout=10000
        )
        self.page.get_by_title(creator_name).first.click()
        self.wait_for_ui_stable()

    @allure.step("选择电商平台：{platform_name}")
    def select_ecommerce_platform(self, platform_name: str) -> None:
        self._select_dropdown_option(
            self.ecommerce_platform_selector,
            platform_name
        )

    @allure.step("选择店铺：{store_name}")
    def select_store(self, store_name: str) -> None:
        self._select_dropdown_option(self.store_selector, store_name)

    @allure.step("填写商品基础信息")
    def fill_product_basic_info(
        self,
        product_id: str,
        product_link: str,
        product_title: str,
        product_name: str,
        delivery_code: str
    ) -> None:
        self._fill_input(self.product_id_input, product_id)
        self._fill_input(self.product_link_input, product_link)
        self._fill_input(self.product_title_input, product_title)
        self._fill_input(self.product_name_input, product_name)
        self._fill_input(self.delivery_code_input, delivery_code)

    @allure.step("设置开群维护：{value}")
    def select_group_maintenance(self, value: str) -> None:
        self._select_dropdown_option(self.group_maintenance_selector, value)

    @allure.step("填写完成天数：{days}")
    def fill_completion_days(self, days: str) -> None:
        self._fill_input(self.completion_days_input, days)

    @allure.step("设置是否评价：{value}")
    def select_review_required(self, value: str) -> None:
        self._select_dropdown_option(self.review_required_selector, value)

    @allure.step("上传工单图片：{image_path}")
    def upload_image(self, image_path: str) -> None:
        self.file_input.wait_for(state="attached", timeout=10000)
        self.file_input.set_input_files(image_path)
        self.wait_for_ui_stable()

    @allure.step("预览首张工单图片")
    def preview_first_image(self) -> None:
        self.preview_image_link.wait_for(state="visible", timeout=10000)
        self.preview_image_link.click(force=True)
        self.wait_for_ui_stable()

    @allure.step("关闭图片预览")
    def close_image_preview(self) -> None:
        self.image_preview_close_button.wait_for(state="visible", timeout=10000)
        self.image_preview_close_button.click(force=True)
        self.wait_for_ui_stable()

    @allure.step("点击添加规格 {count} 次")
    def add_specification_rows(self, count: int = 1) -> None:
        for _ in range(count):
            self._click_and_wait(self.add_specification_button)

    @allure.step("确保规格行数量为 {target_count}")
    def ensure_specification_rows(self, target_count: int) -> None:
        # 页面默认自带一条规格，这里只补足缺少的行数。
        current_count = self.work_order_form.get_by_placeholder("输入规格").count()
        missing_count = max(target_count - current_count, 0)

        if missing_count:
            self.add_specification_rows(missing_count)

    @allure.step("填写第 {index} 条规格")
    def fill_specification(
        self,
        index: int,
        specification: WorkOrderSpecificationData
    ) -> None:
        # 规格按索引逐行填写，避免依赖不稳定的表格结构。
        self._fill_input(
            self.specification_name_input(index),
            specification.name
        )
        self._fill_input(
            self.specification_quantity_input(index),
            specification.quantity
        )
        self._fill_input(
            self.specification_price_input(index),
            specification.price
        )

        if specification.use_current_time:
            appointment_input = self.specification_appointment_input(index)
            appointment_input.wait_for(state="visible", timeout=10000)
            appointment_input.click()
            self.page.get_by_text("此刻", exact=True).last.click()
            self.wait_for_ui_stable()

    @allure.step("填写工单说明")
    def fill_description(self, description: str) -> None:
        self._set_rich_text(description)

    @allure.step("点击保存工单")
    def click_save(self) -> None:
        self._click_and_wait(self.save_button)

    @allure.step("确认保存工单")
    def confirm_save(self) -> None:
        total_count = self.confirm_buttons.count()
        visible_count = self.visible_confirm_buttons.count()
        print(f"[confirm_save] 页面中匹配到 {total_count} 个“确定”按钮")
        print(f"[confirm_save] 当前可见的“确定”按钮有 {visible_count} 个")

        # 先等待保存后的“确定”按钮真正出现。
        print("[confirm_save] 开始等待最后一个“确定”按钮出现")
        self.confirm_button.wait_for(state="visible", timeout=10000)

        # 再点击最后出现的那个“确定”按钮，避免点到页面里原本就有的按钮。
        print("[confirm_save] 已找到最后一个“确定”按钮，准备点击")
        self.confirm_button.click(force=True)

        print("[confirm_save] 已执行点击“确定”按钮")
        # 点击后统一等待页面稳定，方便后续继续观察结果。
        self.wait_for_ui_stable()
        print("[confirm_save] 点击后页面稳定等待完成")

    @allure.step("从组织下的我的工单中发起创建")
    def open_create_work_order(
        self,
        organization_name: str,
        work_order_type: str
    ) -> None:
        self.navigate_to_my_work_orders(organization_name)
        self.click_new_work_order(work_order_type=work_order_type)
        self.select_work_order_type(work_order_type)

    @allure.step("填写工单表单")
    def fill_work_order_form(
        self,
        data: OrganizationWorkOrderCreateData
    ) -> None:
        # 按真实业务顺序依次填写表单。
        if data.proxy_creator:
            self.select_proxy_creator(data.proxy_creator)

        self.select_ecommerce_platform(data.ecommerce_platform)
        self.select_store(data.store_name)
        self.fill_product_basic_info(
            product_id=data.product_id,
            product_link=data.product_link,
            product_title=data.product_title,
            product_name=data.product_name,
            delivery_code=data.delivery_code,
        )
        self.select_group_maintenance(data.group_maintenance)
        self.fill_completion_days(data.completion_days)
        self.select_review_required(data.review_required)

        if data.image_path:
            self.upload_image(data.image_path)

        if data.specifications:
            self.ensure_specification_rows(len(data.specifications))
            for index, specification in enumerate(data.specifications):
                self.fill_specification(index, specification)

        self.fill_description(data.description)

    @allure.step("创建工单")
    def create_work_order(
        self,
        data: OrganizationWorkOrderCreateData,
        preview_image: bool = False
    ) -> None:
        self.open_create_work_order(
            organization_name=data.organization_name,
            work_order_type=data.work_order_type,
        )
        self.fill_work_order_form(data)

        if preview_image and data.image_path:
            self.preview_first_image()
            self.close_image_preview()

        self.click_save()
        self.confirm_save()
