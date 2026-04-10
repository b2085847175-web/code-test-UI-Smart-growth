"""
组织下我的工单操作流测试（先覆盖操作，不做业务断言）。
"""
from dataclasses import replace
from pathlib import Path

import allure
import pytest

from data.work_order_data import build_work_order_create_data
from pages.organization_work_order_page import OrganizationWorkOrderPage
from pages.team_work_order_page import TeamWorkOrderPage


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
        landing_url = logged_in_page.url

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

        # 使用创建工单时生成的时间戳搜索工单，并将工单流转到团队。
        with allure.step("按时间戳搜索工单并流转到团队"):
            work_order_page.transfer_work_order_to_team(
                keyword=work_order_data.search_keyword,
                team_name=work_order_data.resolved_transfer_team_name,
                remark=work_order_data.resolved_transfer_remark,
            )

        # 进入团队工单页，找到刚流转过来的工单，并继续分配给个人处理。
        with allure.step("进入团队工单页并将工单分配给个人"):
            team_work_order_page = TeamWorkOrderPage(logged_in_page)
            team_work_order_page.assign_work_order_to_member(
                base_url=landing_url,
                team_name=work_order_data.organization_name,
                keyword=work_order_data.search_keyword,
                assignee_display_name="赵文龙(18821371697)",
                specification_count=len(work_order_data.specifications),
            )
