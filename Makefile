PYTHON ?= python3

.PHONY: verify verify-package verify-historical verify-route-a

verify-historical:
	PYTHONPATH=. $(PYTHON) verification/replay_release.py

verify-package-historical:
	PYTHONPATH=. $(PYTHON) verification/verify_release.py --check-only

verify-route-a:
	PYTHONPATH=. $(PYTHON) verification/verify_route_a_candidate.py

verify: verify-route-a

verify-package: verify-route-a
