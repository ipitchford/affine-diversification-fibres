"""Scoped release verifier for candidate 0.2.1.

A successful run establishes package integrity and internal replay only. It does
not imply external peer review, theorem truth beyond the stated checks,
statistical coverage or biological validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

import jsonschema
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
VERSION = "0.2.1"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def result(check_id: str, passed: bool, detail: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": "passed" if passed else "failed",
        "detail": detail,
        "evidence": evidence or [],
    }


def validate_records(checks: list[dict[str, Any]]) -> None:
    pairs = [
        (ROOT / "STATUS.json", ROOT / "schemas/status.schema.json"),
        (ROOT / "ASSURANCE.json", ROOT / "schemas/assurance.schema.json"),
        (ROOT / "CLAIM_EVIDENCE.json", ROOT / "schemas/claim_evidence.schema.json"),
    ]
    for record, schema in pairs:
        try:
            jsonschema.Draft202012Validator(load_json(schema)).validate(load_json(record))
            checks.append(result(f"schema:{record.name}", True, "JSON Schema validation passed", [str(record.relative_to(ROOT)), str(schema.relative_to(ROOT))]))
        except Exception as exc:  # pragma: no cover - verifier error path
            checks.append(result(f"schema:{record.name}", False, f"Schema validation failed: {exc}", [str(record.relative_to(ROOT)), str(schema.relative_to(ROOT))]))

    for name in ["AI_INDEX.json", "PROVENANCE.json", "SOURCES.json", "LICENSE_MAP.json", "environment.json", "release_status.json"]:
        path = ROOT / name
        try:
            load_json(path)
            checks.append(result(f"json:{name}", True, "JSON parsed", [name]))
        except Exception as exc:
            checks.append(result(f"json:{name}", False, f"JSON parse failed: {exc}", [name]))


def validate_versions(checks: list[dict[str, Any]]) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pyproject_version = project["project"]["version"]
    namespace: dict[str, Any] = {}
    exec((ROOT / "affine_diversification/affine_fibre.py").read_text(encoding="utf-8"), namespace)
    module_version = namespace.get("__version__")
    status_version = load_json(ROOT / "STATUS.json")["release"]["version"]
    versions = {"pyproject": pyproject_version, "module": module_version, "status": status_version}
    checks.append(result("versions", all(v == VERSION for v in versions.values()), f"Recorded versions: {versions}", ["pyproject.toml", "affine_diversification/affine_fibre.py", "STATUS.json"]))


def validate_claim_paths(checks: list[dict[str, Any]]) -> None:
    claims = load_json(ROOT / "CLAIM_EVIDENCE.json")["claims"]
    missing: list[str] = []
    for claim in claims:
        for item in claim["evidence"]:
            path = item["path"].split("#", 1)[0]
            if not (ROOT / path).exists():
                missing.append(f"{claim['id']}:{path}")
    checks.append(result("claim_evidence_paths", not missing, "All evidence paths resolve" if not missing else f"Missing: {missing}", ["CLAIM_EVIDENCE.json"]))


def validate_unit_tests(checks: list[dict[str, Any]]) -> None:
    proc = run([sys.executable, "-m", "unittest", "affine_diversification.test_affine_fibre", "-v"])
    passed = proc.returncode == 0 and "Ran 17 tests" in proc.stdout and "OK" in proc.stdout
    tail = "\n".join(proc.stdout.strip().splitlines()[-6:])
    checks.append(result("unit_tests", passed, tail, ["affine_diversification/test_affine_fibre.py"]))


def validate_numeric_outputs(checks: list[dict[str, Any]]) -> None:
    independent = load_json(OUT / "independent_checks.json")
    env = independent["envelopes"]
    sim = independent["finite_event_simulation"]
    passed = (
        independent.get("status") == "passed"
        and env.get("random_cases") == 180
        and env.get("target_extrema") == 720
        and env.get("maximum_linear_programme_discrepancy", 1) <= 1e-12
        and abs(sim.get("survival_z", 99)) <= 4
        and sim.get("maximum_conditional_count_absolute_z", 99) <= 4
    )
    checks.append(result("independent_numeric_checks", passed, f"LP max error={env.get('maximum_linear_programme_discrepancy')}; survival |z|={abs(sim.get('survival_z', 99)):.3f}; count max |z|={sim.get('maximum_conditional_count_absolute_z', 99):.3f}", ["outputs/independent_checks.json", "verification/reference_envelopes.py"]))

    negative = load_json(OUT / "negative_controls.json")
    passed = negative.get("status") == "passed" and negative.get("detected") == negative.get("total") == 5
    checks.append(result("negative_controls", passed, f"Detected {negative.get('detected')}/{negative.get('total')} controls", ["outputs/negative_controls.json"]))

    sampling = load_json(OUT / "sampling_comparison_summary.json")
    passed = sampling.get("maximum_exact_empirical_cdf_gap", 1) <= 0.02 and "actual CRABS was not run" in sampling.get("scope_warning", "")
    checks.append(result("sampling_benchmark", passed, f"Exact/Monte Carlo CDF max gap={sampling.get('maximum_exact_empirical_cdf_gap')}; scope warning retained", ["outputs/sampling_comparison_summary.json"]))

    mammal = load_json(OUT / "mammalia_internal_replay.json")
    control = mammal["random_construction_control"]
    passed = (
        mammal.get("internal_software_replay") == "passed"
        and mammal.get("public_curve_reconstruction_max_relative_error", 1) <= 1e-12
        and control.get("histories") == 20000
        and control.get("turnover_violations") == 0
        and control.get("envelope_violations") == 0
        and "not automatically" in mammal.get("interpretive_warning", "")
    )
    checks.append(result("mammal_internal_replay", passed, f"Curve error={mammal.get('public_curve_reconstruction_max_relative_error')}; 20,000 histories; zero violations; interpretation warning retained", ["outputs/mammalia_internal_replay.json"]))


def validate_figures(checks: list[dict[str, Any]]) -> None:
    figures = [f"figure{i}" for i in range(1, 8)]
    alt = load_json(ROOT / "figure_data/ALT_TEXT.json")
    missing: list[str] = []
    for i in range(1, 8):
        matches = list((ROOT / "figures").glob(f"figure{i}_*.png"))
        data_matches = list((ROOT / "figure_data").glob(f"figure{i}_*.csv"))
        if len(matches) != 1:
            missing.append(f"figure{i}:png={len(matches)}")
        if not data_matches:
            missing.append(f"figure{i}:csv=0")
        key = matches[0].name if matches else None
        if key is None or key not in alt or len(str(alt[key]).strip()) < 40:
            missing.append(f"figure{i}:alt")
    checks.append(result("figures_data_alt_text", not missing, "Seven figures have source data and substantive alt text" if not missing else f"Problems: {missing}", ["figures/", "figure_data/ALT_TEXT.json"]))


def validate_pdf(checks: list[dict[str, Any]]) -> None:
    path = ROOT / "manuscript.pdf"
    try:
        reader = PdfReader(path)
        metadata = reader.metadata or {}
        title = str(metadata.get("/Title", ""))
        passed = len(reader.pages) == 16 and title.startswith("Conditional Sharp Partial Identification") and path.stat().st_size > 500_000
        detail = f"pages={len(reader.pages)}; title={title!r}; bytes={path.stat().st_size}; sha256={sha256(path)}"
    except Exception as exc:
        passed, detail = False, f"PDF inspection failed: {exc}"
    checks.append(result("pdf", passed, detail, ["manuscript.pdf", "outputs/pdf_inspection.txt"]))


def validate_wheel(checks: list[dict[str, Any]]) -> None:
    wheels = sorted((ROOT / "dist").glob(f"affine_diversification_fibres-{VERSION}-*.whl"))
    if len(wheels) != 1:
        checks.append(result("wheel", False, f"Expected one {VERSION} wheel, found {len(wheels)}", ["dist/"]))
        return
    wheel = wheels[0]
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "target"
        proc_install = run([sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(target), str(wheel)])
        proc_import = subprocess.run(
            [sys.executable, "-c", f"import sys;sys.path.insert(0,{str(target)!r});import affine_diversification as a;print(a.__version__)"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    passed = proc_install.returncode == 0 and proc_import.returncode == 0 and proc_import.stdout.strip().endswith(VERSION)
    detail = f"wheel={wheel.name}; bytes={wheel.stat().st_size}; sha256={sha256(wheel)}; imported_version={proc_import.stdout.strip().splitlines()[-1] if proc_import.stdout.strip() else 'none'}"
    checks.append(result("wheel", passed, detail, [str(wheel.relative_to(ROOT))]))


def validate_no_broad_pass(checks: list[dict[str, Any]]) -> None:
    forbidden = ROOT / "outputs/verification_report.json"
    status = load_json(ROOT / "STATUS.json")
    passed = (
        not forbidden.exists()
        and status["release"]["publication_ready"]
        and status["release"]["state"] == "candidate"
        and status["release"].get("publication_readiness_scope") == "public_candidate_dissemination_only"
    )
    checks.append(result(
        "assurance_scope",
        passed,
        "No generic verification_report.json; state remains candidate; publication_ready is scoped to public candidate dissemination only",
        ["STATUS.json", "ASSURANCE.json"],
    ))


def validate_manifest(checks: list[dict[str, Any]]) -> None:
    path = ROOT / "MANIFEST.sha256"
    if not path.exists():
        checks.append(result("manifest", True, "Manifest not yet present; skipped during pre-manifest verifier run", []))
        return
    bad: list[str] = []
    listed: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        listed.add(rel)
        target = ROOT / rel
        if not target.exists() or sha256(target) != digest:
            bad.append(rel)
    def generated(path: Path) -> bool:
        relative = path.relative_to(ROOT)
        return relative.as_posix() == "REPLAY_RECEIPT.json" or any(
            part in {".git", ".venv", "build", "__pycache__"}
            or part.endswith(".egg-info")
            for part in relative.parts
        ) or path.suffix == ".pyc"

    payload = {
        str(p.relative_to(ROOT))
        for p in ROOT.rglob("*")
        if p.is_file() and p.name != "MANIFEST.sha256" and not generated(p)
    }
    missing = sorted(payload - listed)
    extra = sorted(listed - payload)
    passed = not bad and not missing and not extra
    checks.append(result("manifest", passed, f"listed={len(listed)}; bad_hashes={bad}; missing={missing}; extra={extra}", ["MANIFEST.sha256"]))


def validate_replay_receipt(checks: list[dict[str, Any]]) -> None:
    path = ROOT / "REPLAY_RECEIPT.json"
    if not path.exists():
        checks.append(result("replay_receipt", False, "REPLAY_RECEIPT.json is missing", []))
        return
    try:
        receipt = load_json(path)
        recorded_manifest = receipt.get("manifest_sha256")
        current_manifest = sha256(ROOT / "MANIFEST.sha256")
        passed = receipt.get("status") == "passed" and recorded_manifest == current_manifest
        detail = (
            f"status={receipt.get('status')}; manifest_sha256_match="
            f"{recorded_manifest == current_manifest}; receipt is archive-bound rather than self-listed"
        )
    except Exception as exc:
        passed, detail = False, f"Receipt validation failed: {exc}"
    checks.append(result("replay_receipt", passed, detail, ["REPLAY_RECEIPT.json", "MANIFEST.sha256"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true", help="Do not rewrite outputs/release_verification.json")
    parser.add_argument(
        "--replay-scratch",
        action="store_true",
        help="Validate regenerated outputs in a disposable copy; manifest integrity must have passed before the copy was made",
    )
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    validate_records(checks)
    validate_versions(checks)
    validate_claim_paths(checks)
    validate_unit_tests(checks)
    validate_numeric_outputs(checks)
    validate_figures(checks)
    validate_pdf(checks)
    validate_wheel(checks)
    validate_no_broad_pass(checks)
    if not args.replay_scratch:
        validate_manifest(checks)
        validate_replay_receipt(checks)

    failures = [c for c in checks if c["status"] != "passed"]
    report = {
        "schema_version": "1.0",
        "release": VERSION,
        "scope": (
            "regenerated-output semantic replay in a disposable copy"
            if args.replay_scratch
            else "frozen package integrity and shipped-output checks"
        ),
        "explicit_nonclaims": [
            "external peer review",
            "formal proof verification",
            "statistical confidence coverage",
            "fossil observation validation",
            "exhaustive novelty",
            "actual CRABS comparison",
        ],
        "status": "passed" if not failures else "failed",
        "checks_passed": len(checks) - len(failures),
        "checks_total": len(checks),
        "checks": checks,
    }
    if not args.check_only:
        OUT.mkdir(exist_ok=True)
        (OUT / "release_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
