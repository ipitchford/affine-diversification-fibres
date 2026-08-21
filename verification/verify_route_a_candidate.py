"""Verify the Route A review candidate without rewriting historical receipts.

This establishes scoped internal consistency and repeatability.  It is not an
external process-theory review, independent reproduction, rights approval, or
authorization to publish.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import jsonschema
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/route_a_candidate_verification.json"
EXPECTED_VERSION = "0.3.0rc2"
RELEASE_DOI = "10.5281/zenodo.22041054"
HISTORICAL_HASHES = {
    "MANIFEST.sha256": "6c50d82213472a29eae71a22839f8addf023ad37238232473198f33d4ddb0f77",
    "REPLAY_RECEIPT.json": "aa596334df3bed17d264bab30da88e8ed674790a2347271834be3236868013d2",
}
SEALED_HASHES = {
    "experiments/affine_crabs_confirmatory/execution/STOCHASTIC_STAGE2_MANIFEST.sha256": "1a751b4500ce28eb14db6a44773c73727a76aca96d001273af0507f4f06b31d2",
    "experiments/affine_crabs_confirmatory/execution/STOCHASTIC_STAGE2_EXECUTION_RECEIPT.json": "7553aab3309a08cf2ed25b0ace182edd81b3ebd9a14f59a10f49e538cfabeb77",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def check(check_id: str, passed: bool, detail: str, evidence: list[str]) -> dict[str, Any]:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail, "evidence": evidence}


def run_tests(optimized: bool) -> tuple[bool, str]:
    command = [sys.executable]
    if optimized:
        command.append("-O")
    command.extend(["-m", "unittest", "affine_diversification.test_affine_fibre", "-v"])
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    process = subprocess.run(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    output_name = "route_a_unit_tests_optimized.txt" if optimized else "route_a_unit_tests_normal.txt"
    (ROOT / "outputs" / output_name).write_text(process.stdout, encoding="utf-8")
    passed = process.returncode == 0 and "Ran 21 tests" in process.stdout and process.stdout.rstrip().endswith("OK")
    return passed, "\n".join(process.stdout.rstrip().splitlines()[-6:])


def validate_manifest(relative: str) -> tuple[bool, str]:
    lines = (ROOT / relative).read_text(encoding="utf-8").splitlines()
    failures: list[str] = []
    for line in lines:
        expected, path_text = line.split("  ", 1)
        path = ROOT / path_text
        if not path.is_file() or sha256(path) != expected:
            failures.append(path_text)
            if len(failures) == 5:
                break
    return not failures, f"validated {len(lines)} entries" if not failures else f"first mismatches: {failures}"


def main() -> int:
    checks: list[dict[str, Any]] = []

    project_version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    namespace: dict[str, Any] = {}
    exec((ROOT / "affine_diversification/affine_fibre.py").read_text(encoding="utf-8"), namespace)
    status_version = load_json("STATUS.json")["release"]["version"]
    versions = {"pyproject": project_version, "module": namespace.get("__version__"), "status": status_version}
    checks.append(check("version_coherence", all(value == EXPECTED_VERSION for value in versions.values()), str(versions), ["pyproject.toml", "affine_diversification/affine_fibre.py", "STATUS.json"]))

    for record, schema in [("STATUS.json", "schemas/status.schema.json"), ("ASSURANCE.json", "schemas/assurance.schema.json"), ("CLAIM_EVIDENCE.json", "schemas/claim_evidence.schema.json")]:
        try:
            jsonschema.Draft202012Validator(load_json(schema)).validate(load_json(record))
            checks.append(check(f"schema:{record}", True, "schema validation passed", [record, schema]))
        except Exception as exc:
            checks.append(check(f"schema:{record}", False, str(exc), [record, schema]))

    json_records = [".zenodo.json", "AI_INDEX.json", "PROVENANCE.json", "environment.json", "SOURCES.json", "LICENSE_MAP.json", "PUBLICATION_STATE.json", "release_status.json", "figure_data/ALT_TEXT.json", "review/route_a/SOURCES_ROUTE_A.json", "review/route_a/ROUTE_A_REVISION_HASHES.json"]
    try:
        for record in json_records:
            load_json(record)
        checks.append(check("json_records", True, f"parsed {len(json_records)} successor records", json_records))
    except Exception as exc:
        checks.append(check("json_records", False, str(exc), json_records))

    doi_surfaces = {
        "CITATION.cff": (ROOT / "CITATION.cff").read_text(encoding="utf-8"),
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "manuscript.tex": (ROOT / "manuscript.tex").read_text(encoding="utf-8"),
        "manuscript.md": (ROOT / "manuscript.md").read_text(encoding="utf-8"),
    }
    structured_dois = {
        "STATUS.json": load_json("STATUS.json")["release"]["doi_for_this_candidate"],
        "AI_INDEX.json": load_json("AI_INDEX.json")["persistent_identifier"],
        "PROVENANCE.json": load_json("PROVENANCE.json")["persistent_identifier"],
        "release_status.json": load_json("release_status.json")["doi"],
        "PUBLICATION_STATE.json": load_json("PUBLICATION_STATE.json")["zenodo"]["versionDoi"],
    }
    zenodo_metadata = load_json(".zenodo.json")
    doi_pass = (
        all(RELEASE_DOI in text for text in doi_surfaces.values())
        and all(RELEASE_DOI in value for value in structured_dois.values())
        and zenodo_metadata["version"] == "0.3.0-candidate-r2"
        and zenodo_metadata["creators"] == [{"name": "Anonymous"}]
    )
    checks.append(check("release_identity_coherence", doi_pass, f"doi={RELEASE_DOI}; structured={structured_dois}; zenodo_version={zenodo_metadata['version']}", [*doi_surfaces, *structured_dois, ".zenodo.json"]))

    hash_results = {path: sha256(ROOT / path) for path in {**HISTORICAL_HASHES, **SEALED_HASHES}}
    hashes_pass = all(hash_results[path] == expected for path, expected in {**HISTORICAL_HASHES, **SEALED_HASHES}.items())
    checks.append(check("protected_hashes", hashes_pass, str(hash_results), list(hash_results)))

    ledger_pass, ledger_detail = validate_manifest("experiments/affine_crabs_confirmatory/execution/STOCHASTIC_STAGE2_MANIFEST.sha256")
    checks.append(check("sealed_stage2_ledger", ledger_pass, ledger_detail, ["experiments/affine_crabs_confirmatory/execution/STOCHASTIC_STAGE2_MANIFEST.sha256"]))

    release_manifest_pass, release_manifest_detail = validate_manifest("RELEASE_MANIFEST.sha256")
    checks.append(check("successor_release_manifest", release_manifest_pass, release_manifest_detail, ["RELEASE_MANIFEST.sha256"]))

    fixed = load_json("outputs/fixed_stem_uncertainty.json")
    fixed_pass = (
        fixed["observed_tree"]["n_tips"] == 22
        and fixed["primary_target"]["status"] == "CERTIFIED_INCOMPATIBLE"
        and fixed["caution_target"]["plugin_status"] == "PLUGIN_COMPATIBLE"
        and fixed["caution_target"]["status"] == "UNRESOLVED"
        and fixed["coverage_sanity_check"]["replicates"] == 20000
        and fixed["coverage_sanity_check"]["joint_component_coverage"] >= fixed["coverage_sanity_check"]["nominal_joint_lower_bound"]
    )
    checks.append(check("route_a_frozen_decision", fixed_pass, f"N={fixed['observed_tree']['n_tips']}; primary={fixed['primary_target']['status']}; caution={fixed['caution_target']['status']}; joint={fixed['coverage_sanity_check']['joint_component_coverage']}", ["outputs/fixed_stem_uncertainty.json"]))

    benchmark = load_json("outputs/crabs_h2_h4_revision_summary.json")
    matrix = benchmark["H4"]["transition_matrix"]
    matrix_total = sum(sum(row.values()) for row in matrix.values())
    changed_total = sum(value for source, row in matrix.items() for target, value in row.items() if source != target)
    benchmark_pass = (
        benchmark["H2"]["returned_clouds"] == benchmark["H2"]["returned_cloud_deficit_events"] == 240
        and benchmark["H2"]["structural_censors"] == 60
        and matrix_total == benchmark["H4"]["evaluable_queries"] == 3840
        and changed_total == benchmark["H4"]["changed_queries"] == 532
    )
    checks.append(check("h2_h4_invariants", benchmark_pass, f"H2=240/240 plus 60 censors; H4={changed_total}/{matrix_total}", ["outputs/crabs_h2_h4_revision_summary.json", "figure_data/crabs_h4_status_transitions.csv"]))

    with (ROOT / "figure_data/crabs_h4_status_transitions.csv").open(newline="", encoding="utf-8") as handle:
        transition_rows = list(csv.DictReader(handle))
    with (ROOT / "figure_data/crabs_h4_transition_strata.csv").open(newline="", encoding="utf-8") as handle:
        strata_rows = list(csv.DictReader(handle))
    strata = {row["stratum"] for row in strata_rows}
    h4_tables_pass = len(transition_rows) == 9 and len(strata) == 24 and len(strata_rows) == 24 * 9
    checks.append(check("h4_tables", h4_tables_pass, f"pooled transition rows={len(transition_rows)}; strata={len(strata)}; stratum-transition rows={len(strata_rows)}", ["figure_data/crabs_h4_status_transitions.csv", "figure_data/crabs_h4_transition_strata.csv"]))

    alt = load_json("figure_data/ALT_TEXT.json")
    figure_files = sorted(path.name for path in (ROOT / "figures").glob("*.png"))
    missing_alt = [name for name in figure_files if name not in alt]
    checks.append(check("figure_alt_text", not missing_alt, f"PNG figures={len(figure_files)}; missing={missing_alt}", ["figure_data/ALT_TEXT.json", "figures/"]))

    reader = PdfReader(ROOT / "manuscript.pdf")
    pdf_pass = len(reader.pages) == 23 and "Finite-Sample Signal Uncertainty" in (reader.metadata.title or "")
    checks.append(check("pdf", pdf_pass, f"pages={len(reader.pages)}; title={reader.metadata.title}", ["manuscript.pdf", "outputs/pdf_inspection_route_a.txt"]))

    markdown = (ROOT / "manuscript.md").read_text(encoding="utf-8")
    markdown_pass = markdown.startswith("# Finite-Sample Signal Uncertainty") and "## Abstract" in markdown and "Theorem 14" in markdown
    checks.append(check("accessible_markdown", markdown_pass, "title, abstract and stable Route A theorem locator present", ["manuscript.md"]))

    status = load_json("STATUS.json")
    publication_ready = status["release"]["publication_ready"]
    public_authorizations = load_json("PUBLICATION_STATE.json")["authorization"]
    expected_authorizations = ["publicGitHub", "zenodoDraft", "zenodoPublish", "evidencePressDeploy"]
    publication_boundary_pass = (
        publication_ready is True
        and status["release"].get("publication_readiness_scope") == "unrefereed_evidence_press_candidate_pass_with_notes"
        and all(public_authorizations.get(key) is True for key in expected_authorizations)
        and bool(public_authorizations.get("basis"))
        and load_json("ASSURANCE.json")["items"][2]["status"] == "not_assessed"
    )
    checks.append(check("publication_boundary", publication_boundary_pass, f"publication_ready={publication_ready}; scope={status['release'].get('publication_readiness_scope')}; public authorizations={public_authorizations}", ["STATUS.json", "ASSURANCE.json", "PUBLICATION_STATE.json"]))

    license_map = load_json("LICENSE_MAP.json")
    mit_paths = next((item["paths"] for item in license_map["components"] if item["license"] == "MIT"), [])
    license_pass = (ROOT / "LICENSE-CODE").is_file() and "affine_diversification/**" in mit_paths and any(item["license"] == "NOASSERTION" for item in license_map["components"])
    checks.append(check("component_licensing", license_pass, f"MIT paths={len(mit_paths)}; NOASSERTION exceptions preserved", ["LICENSE", "LICENSE-CODE", "LICENSE.md", "LICENSE_MAP.json"]))

    normal_pass, normal_tail = run_tests(False)
    optimized_pass, optimized_tail = run_tests(True)
    checks.append(check("unit_tests_normal", normal_pass, normal_tail, ["outputs/route_a_unit_tests_normal.txt"]))
    checks.append(check("unit_tests_optimized", optimized_pass, optimized_tail, ["outputs/route_a_unit_tests_optimized.txt"]))

    required_review_files = [f"review/route_a/{name}" for name in ["00_REVISION_CONFIGURATION.md", "01_RESPONSE_TO_REVIEWERS.md", "02_CHANGE_LOG.md", "03_EXTERNAL_PROCESS_REVIEW_REQUEST.md", "04_INDEPENDENT_REPLAY_REQUEST.md", "05_RIGHTS_REVIEW_CHECKLIST.md", "06_STAGE4_CHECKPOINT.md"]]
    checks.append(check("review_packet", all((ROOT / path).is_file() for path in required_review_files), "R1-R9/S1-S6 response and open-gate requests present", required_review_files))

    stage3_prime_pass, stage3_prime_detail = validate_manifest("review/stage3_prime/STAGE3_PRIME_MANIFEST.sha256")
    stage3_prime_pass = stage3_prime_pass and (ROOT / "docs/final_integrity_report_20260821.md").is_file()
    checks.append(check("stage3_prime_and_final_integrity", stage3_prime_pass, stage3_prime_detail, ["review/stage3_prime/STAGE3_PRIME_MANIFEST.sha256", "docs/final_integrity_report_20260821.md"]))

    overall = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    result = {
        "schema_version": "1.0",
        "candidate": EXPECTED_VERSION,
        "status": overall,
        "assurance_boundary": "Internal candidate verification only; not external theorem review, independent reproduction, rights approval or publication authorization.",
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
