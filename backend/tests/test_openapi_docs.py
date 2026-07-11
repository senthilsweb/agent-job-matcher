"""
File Name: test_openapi_docs.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
OpenAPI documentation gate (no LLM) — AGENTS.md rule 9 and
openspec/changes/add-openapi-release-artifact/: an undocumented endpoint
is a failing build, not a review comment.

This suite pins the contract by:
1. Every path+method carries a non-empty summary and description.
2. Every operation has a response example; body-accepting operations
   document their request schema.
3. info carries the project description, version, license, contact;
   externalDocs links the repo.
4. The generated document passes openapi-spec-validator.
"""

# Import necessary libraries
from job_matcher import __version__
from job_matcher.api import app

METHODS = {"get", "post", "put", "patch", "delete"}


def spec() -> dict:
    return app.openapi()


def test_every_operation_documented():
    for path, item in spec()["paths"].items():
        for method, op in item.items():
            if method not in METHODS:
                continue
            assert op.get("summary"), f"{method.upper()} {path} missing summary"
            assert op.get("description"), f"{method.upper()} {path} missing description"


def test_every_operation_has_response_example():
    for path, item in spec()["paths"].items():
        for method, op in item.items():
            if method not in METHODS:
                continue
            ok = op.get("responses", {}).get("200", {})
            content = ok.get("content", {}).get("application/json", {})
            assert "example" in content or "examples" in content, (
                f"{method.upper()} {path} missing a 200 response example"
            )


def test_body_operations_document_request():
    for path, item in spec()["paths"].items():
        for method, op in item.items():
            if method not in METHODS or method == "get":
                continue
            assert "requestBody" in op, f"{method.upper()} {path} missing requestBody schema"


def test_info_and_repo_link():
    s = spec()
    info = s["info"]
    assert "deterministically scored" in info["description"]
    assert info["version"] == __version__
    assert info["license"]["name"] == "MIT"
    assert info["contact"]["url"]
    assert s["externalDocs"]["url"] == "https://github.com/senthilsweb/agent-job-matcher"


def test_spec_validates():
    from openapi_spec_validator import validate

    validate(spec())
