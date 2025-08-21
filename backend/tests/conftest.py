"""Test configuration for backend package."""

import sys
import types
from pathlib import Path


# Provide a lightweight stub for the external `frappe_client` dependency so
# that backend modules can be imported without the actual package being
# installed. The tests patch the client where needed, so only the class name is
# required here.
class _DummyFrappeClient:  # pragma: no cover - simple shim
	def __init__(self, *args, **kwargs):
		pass


frappe_module = types.ModuleType("frappe_client")
frappe_module.FrappeClient = _DummyFrappeClient  # type: ignore[attr-defined]
sys.modules.setdefault("frappe_client", frappe_module)

# Ensure that the project root is on the Python path so that `import backend`
# works when tests are executed from within the package directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))
