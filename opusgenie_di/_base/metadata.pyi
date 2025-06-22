from datetime import datetime
from typing import Any

from pydantic import BaseModel

from .enums import ComponentLayer, LifecycleStage

class ComponentMetadata(BaseModel):
    component_id: str
    component_type: str
    component_name: str | None
    layer: ComponentLayer | None
    lifecycle_stage: LifecycleStage
    created_at: datetime
    updated_at: datetime | None
    tags: dict[str, str]
    config: dict[str, Any]
    context_name: str

    def __init__(self, **data: Any) -> None: ...
