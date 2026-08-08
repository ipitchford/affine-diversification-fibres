PYTHON ?= python3

.PHONY: verify verify-package

verify:
	PYTHONPATH=. $(PYTHON) verification/replay_release.py

verify-package:
	PYTHONPATH=. $(PYTHON) verification/verify_release.py --check-only
