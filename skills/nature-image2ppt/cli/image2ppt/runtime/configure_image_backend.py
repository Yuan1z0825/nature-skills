#!/usr/bin/env python3
import argparse
import json
import os

from deck_run_state import load_deck, load_jobs, read_json, run_dir_from_target, save_deck, write_json
from runtime_env import DEFAULT_IMAGE_MODEL, config_path, read_config_file


def configured_model() -> str:
    """Resolve the provider model without assuming any vendor-specific id."""
    values = read_config_file(config_path())
    return str(os.getenv("IMAGE2PPT_IMAGE_MODEL") or values.get("IMAGE2PPT_IMAGE_MODEL") or DEFAULT_IMAGE_MODEL).strip()


def backend_contract(args):
    is_builtin = args.backend_id == "builtin-imagegen"
    requires_api_key = args.backend_id == "openai-compatible-api"
    contract = {
        "backend_id": args.backend_id,
        "tool_name": args.tool_name,
        "tool_call": args.tool_call,
        "fallback_command": args.fallback_command,
        "runtime_home": args.runtime_home,
        "model": None if is_builtin else args.model,
        "requires_openai_api_key": requires_api_key,
        "mode_policy": "generate-or-edit-per-asset",
        "chroma_key_helper": "image2ppt image process-sheet",
        "input_context_policy": args.input_context_policy,
        "save_path_policy": (
            "accept only an explicit output_hint or local path returned by image_gen.imagegen, verify it exists, "
            "import the selected output, and never scan for the newest file"
            if is_builtin
            else "write outputs directly to page dir or copy selected outputs before manifest references them"
        ),
        "handoff_rule": (
            "call image_gen.imagegen serially, then import the selected local output; "
            "use image2ppt image generate/edit only when the built-in tool fallback policy applies"
            if is_builtin
            else "call image2ppt image generate/edit serially; --backend or IMAGE2PPT_IMAGE_BACKEND selects Codex OAuth versus an OpenAI Images-compatible API"
        ),
    }
    if is_builtin:
        contract.update(
            {
                "fallback_order": ["codex-oauth", "openai-compatible-api"],
                "fallback_selection_policy": (
                    "auto uses codex-oauth only for GPT Image model ids with compatible auth; "
                    "all other model ids use openai-compatible-api"
                ),
                "required_parameters": {
                    "generate": ["prompt"],
                    "edit": ["prompt", "referenced_image_paths"],
                },
                "fallback_policy": {
                    "on": [
                        "tool-unavailable",
                        "tool-error",
                        "input-unreadable",
                        "no-valid-local-output",
                    ],
                    "missing_optional_parameters": False,
                },
            }
        )
    return contract


def main():
    parser = argparse.ArgumentParser(description="Record the run-level image backend contract.")
    parser.add_argument("run")
    parser.add_argument(
        "--backend-id",
        default="image2ppt-image-cli",
        choices=["builtin-imagegen", "image2ppt-image-cli", "openai-compatible-api"],
    )
    parser.add_argument("--tool-name")
    parser.add_argument("--tool-call")
    parser.add_argument(
        "--model",
        default=None,
        help="Exact provider model id. Defaults to IMAGE2PPT_IMAGE_MODEL from the active config/environment.",
    )
    parser.add_argument("--fallback-command")
    parser.add_argument("--runtime-home", default=None)
    parser.add_argument("--input-context-policy")
    args = parser.parse_args()

    if args.model is None:
        args.model = configured_model()
    if not args.model:
        parser.error("--model or IMAGE2PPT_IMAGE_MODEL must be a non-empty provider model id")
    if args.runtime_home is None:
        args.runtime_home = str(config_path().parent)

    if args.backend_id == "builtin-imagegen":
        fixed_field_overrides = [
            flag
            for flag, value in (
                ("--tool-name", args.tool_name),
                ("--tool-call", args.tool_call),
                ("--fallback-command", args.fallback_command),
                ("--input-context-policy", args.input_context_policy),
            )
            if value is not None
        ]
        if fixed_field_overrides:
            parser.error(
                f"{', '.join(fixed_field_overrides)} cannot override the fixed builtin-imagegen contract"
            )
        args.tool_name = "image_gen.imagegen"
        args.tool_call = "image_gen.imagegen"
        args.fallback_command = "image2ppt image generate/edit"
        args.input_context_policy = (
            "generation needs prompt; for editing inspect every local input with view_image first, then pass "
            "prompt plus absolute local paths in referenced_image_paths"
        )
    else:
        if args.tool_name is None:
            args.tool_name = "image2ppt image"
        if args.tool_call is None:
            args.tool_call = "image2ppt image generate/edit"
        if args.fallback_command is None:
            args.fallback_command = "image2ppt image"
        if args.input_context_policy is None:
            args.input_context_policy = "pass edit targets and strict visual references via image2ppt image edit --image"

    run_dir = run_dir_from_target(args.run)
    deck = load_deck(run_dir)
    contract = backend_contract(args)
    deck["image_backend"] = contract
    save_deck(run_dir, deck)

    jobs = load_jobs(run_dir)
    for page in jobs.get("pages", []):
        request_path = run_dir / page["page_request"]
        request = read_json(request_path)
        request["image_backend"] = contract
        write_json(request_path, request)
    print(json.dumps({"image_backend": contract}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
