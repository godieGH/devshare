import importlib.metadata
import os
import re

try:
	__version__ = importlib.metadata.version("devshare")
except Exception:
	try:
		here = os.path.dirname(__file__)
		root = os.path.abspath(os.path.join(here, ".."))
		with open(os.path.join(root, "pyproject.toml"), "r", encoding="utf-8") as f:
			content = f.read()
		match = re.search(r"^version\s*=\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE)
		__version__ = match.group(1) if match else "0.0.0"
	except Exception:
		__version__ = "0.0.0"