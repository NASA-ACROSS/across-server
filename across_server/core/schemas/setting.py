from ...core.enums.setting_type import SettingType
from ...core.schemas.base import BaseSchema


class Setting(BaseSchema):
    name: str
    value: str
    display_name: str | None
    type: SettingType
