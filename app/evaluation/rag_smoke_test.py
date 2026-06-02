from app.rag.retriever import retrieve_policy_evidence


def main() -> None:
    result = retrieve_policy_evidence(
        case_id="TEST_CASE_001",
        query="Failed settlement due to SSI mismatch for US equity trade. Need validation steps and escalation guidance.",
        exception_type="SSI_MISMATCH",
        market="US",
    )

    print("RAG smoke test completed")
    print("retrieval_confidence:", result.retrieval_confidence)
    print("citations:")
    for citation in result.citations:
        print(citation.model_dump())


if __name__ == "__main__":
    main()