import os

from app.services.llm import EchoLLMClient, StubLLMClient, get_llm_client


def test_stub_llm_generates_stub_marker():
    out = StubLLMClient().generate(query="retrieval", contexts=["alpha context"])
    assert out.model == "stub-rag-v5"
    assert "[STUB]" in out.text


def test_echo_llm_generates_echo_marker():
    out = EchoLLMClient().generate(query="retrieval", contexts=["alpha", "beta"])
    assert out.model == "echo-local-v1"
    assert out.text.startswith("[ECHO]")


def test_get_llm_client_env_switch():
    os.environ["RACHEL_LLM_PROVIDER"] = "echo"
    client = get_llm_client()
    assert isinstance(client, EchoLLMClient)
    os.environ["RACHEL_LLM_PROVIDER"] = "stub"
