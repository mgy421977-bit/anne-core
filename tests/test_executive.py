from anne_core.executive.executive import ExecutiveANNE
from anne_core.memory.models import CognitiveStructure


def test_executive_surfaces_agreement_contradiction_and_provenance():
    structure = CognitiveStructure(
        concept="test",
        question="test question",
        findings=["A concise primary finding.", "A longer provider finding with supporting detail."],
        sources=["mock-A", "mock-B"],
        agreement=["Both providers agree on the core mechanism."],
        contradictions=["Providers disagree about one secondary detail."],
        confidence=0.72,
        evidence=["[mock-A] conf=0.90 evidence=strong"],
        reusable=True,
    )

    output = ExecutiveANNE().synthesise(structure)
    assert "Primary evaluated finding" in output
    assert "Points supported across sources" in output
    assert "Unresolved divergences / open questions" in output
    assert "Evidence / provenance trail" in output
    assert "0.72" in output
