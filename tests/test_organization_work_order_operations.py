"""
组织下我的工单操作流测试（先覆盖操作，不做业务断言）。
"""
from dataclasses import replace
from pathlib import Path

import allure
import pytest

from data.work_order_data import build_work_order_create_data
from pages.organization_work_order_page import OrganizationWorkOrderPage


@allure.epic("工单管理模块")
@allure.feature("组织下我的工单操作")
class TestOrganizationWorkOrderOperations:
    """组织下我的工单操作测试类"""

    @allure.story("创建工单主流程")
    @allure.title("登录后进入组织下的我的工单并完成创建工单操作")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_work_order_in_my_work_orders(self, logged_in_page):
        """
        测试步骤：
            1. 进入指定组织
            2. 进入我的工单
            3. 点击新建工单并选择工单类型
            4. 填写工单基础信息
            5. 上传图片并预览（文件存在时）
            6. 添加规格并填写明细
            7. 填写工单说明并保存确认
        """
        work_order_page = OrganizationWorkOrderPage(logged_in_page)
        work_order_data = build_work_order_create_data()

        project_root = Path(__file__).resolve().parents[1]
        image_path = None
        if work_order_data.image_path:
            candidate = project_root / work_order_data.image_path
            if candidate.exists():
                image_path = str(candidate)

        if image_path != work_order_data.image_path:
            work_order_data = replace(work_order_data, image_path=image_path)

        with allure.step("步骤1-7：完成组织下我的工单创建流程"):
            work_order_page.create_work_order(
                data=work_order_data,
                preview_image=bool(work_order_data.image_path),
            )
