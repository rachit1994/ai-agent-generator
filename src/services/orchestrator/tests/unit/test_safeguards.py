from sde.safeguards import validate_structured_output, validate_task_text


def test_rejects_empty_task() -> None:
    try:
        validate_task_text(" ")
    except ValueError as exc:
        assert "invalid_input_empty_task" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_parses_fenced_json_output() -> None:
    payload = "```json\n{\"answer\":\"ok\",\"checks\":[{\"name\":\"format\",\"passed\":true}],\"refusal\":null}\n```"
    parsed = validate_structured_output(payload)
    assert parsed["answer"] == "ok"
    assert parsed["checks"][0]["passed"] is True


def test_normalizes_empty_checks_and_refusal_list() -> None:
    payload = "```json\n{\"answer\":\"hello\",\"checks\":[],\"refusal\":[]}\n```"
    parsed = validate_structured_output(payload)
    assert parsed["checks"][0]["name"] == "response_non_empty"
    assert parsed["checks"][0]["passed"] is True
    assert parsed["refusal"] is None
