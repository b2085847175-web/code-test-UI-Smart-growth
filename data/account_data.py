"""
账号管理相关测试数据与动态数据构造。
"""
from dataclasses import dataclass, asdict
import time

DEFAULT_ACCOUNT_PASSWORD = "Ww12345678.."
DEFAULT_ROLE = "普通成员"
DEFAULT_IDENTITY_TYPE = "内部用户"


@dataclass(frozen=True)
class AccountCreateData:
    name: str
    password: str
    phone: str
    role: str
    identity_type: str


def build_account_create_data() -> dict:
    """
    生成唯一账号数据，避免创建冲突。
    """
    ts = int(time.time() * 1000)
    suffix = str(ts)[-6:]
    # 11 位手机号，首位固定 1
    phone = f"1{str(ts % 10**10).zfill(10)}"

    data = AccountCreateData(
        name=f"auto_{suffix}",
        password=DEFAULT_ACCOUNT_PASSWORD,
        phone=phone,
        role=DEFAULT_ROLE,
        identity_type=DEFAULT_IDENTITY_TYPE,
    )
    return asdict(data)
