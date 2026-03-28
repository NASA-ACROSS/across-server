from __future__ import annotations

from typing import Any

from across.tools.visibility.constraints import Constraint as ToolsConstraint
from pydantic import RootModel, TypeAdapter

_tools_constraint_adapter: TypeAdapter[ToolsConstraint] = TypeAdapter(ToolsConstraint)


class Constraint(RootModel[dict[str, Any]]):
    def to_tools_constraint(self) -> ToolsConstraint:
        return _tools_constraint_adapter.validate_python(self.root)
