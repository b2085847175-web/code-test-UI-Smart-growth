"""
组织下创建工单的数据结构。
"""
from dataclasses import dataclass
from typing import Optional, Tuple
import time


@dataclass(frozen=True)
class WorkOrderSpecificationData:
    """
    工单规格行数据。
    """

    name: str
    quantity: str
    price: str
    use_current_time: bool = True


@dataclass(frozen=True)
class OrganizationWorkOrderCreateData:
    """
    组织下创建工单的基础数据。
    """

    organization_name: str
    work_order_type: str
    ecommerce_platform: str
    store_name: str
    product_id: str
    product_link: str
    product_title: str
    product_name: str
    delivery_code: str
    group_maintenance: str
    completion_days: str
    review_required: str
    description: str
    proxy_creator: Optional[str] = None
    image_path: Optional[str] = None
    specifications: Tuple[WorkOrderSpecificationData, ...] = ()


def build_work_order_create_data(
    organization_name: str = "自动化测试专用",
    work_order_type: str = "提前购",
    proxy_creator: Optional[str] = "赵文龙",
    ecommerce_platform: str = "淘宝/天猫",
    store_name: str = "儒意旗舰店",
    group_maintenance: str = "是",
    completion_days: str = "30",
    review_required: str = "是",
    description: str = "工单说明",
    image_path: Optional[str] = "屏幕截图(1).png",
) -> OrganizationWorkOrderCreateData:
    """
    生成一份默认的创建工单数据，方便测试直接复用。
    """
    timestamp = time.strftime("%Y%m%d%H%M")

    return OrganizationWorkOrderCreateData(
        organization_name=organization_name,
        work_order_type=work_order_type,
        proxy_creator=proxy_creator,
        ecommerce_platform=ecommerce_platform,
        store_name=store_name,
        product_id=timestamp,
        product_link=f"https://{timestamp}",
        product_title=f"商品标题test{timestamp}",
        product_name=f"商品名称test{timestamp}",
        delivery_code=timestamp,
        group_maintenance=group_maintenance,
        completion_days=completion_days,
        review_required=review_required,
        description=description,
        image_path=image_path,
        specifications=(
            WorkOrderSpecificationData(name="规格1", quantity="1", price="20"),
            WorkOrderSpecificationData(name="规格2", quantity="1", price="21"),
            WorkOrderSpecificationData(name="规格3", quantity="1", price="22"),
        ),
    )
