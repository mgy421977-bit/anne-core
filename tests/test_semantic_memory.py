from anne_core.memory.models import CognitiveStructure
from anne_core.memory.semantic import LightweightSemanticMatcher, cosine_similarity
from anne_core.memory.sqlite import CognitiveMemory


def test_similarity_is_deterministic_and_paraphrase_tolerant():
    a = "What are the main causes of urban heat islands?"
    b = "Which factors create the urban heat island effect?"
    unrelated = "How does photosynthesis convert sunlight into chemical energy?"

    score = cosine_similarity(a, b)
    assert score == cosine_similarity(a, b)
    assert score > cosine_similarity(a, unrelated)
    assert LightweightSemanticMatcher(threshold=0.10).is_relevant(score)


def test_semantic_memory_returns_candidate_with_score(tmp_path):
    memory = CognitiveMemory(db_path=str(tmp_path / "memory.db"), semantic_threshold=0.20)
    structure = CognitiveStructure(
        concept="urban heat islands",
        question="What causes urban heat islands?",
        findings=["Built surfaces retain heat and reduced vegetation limits cooling."],
        confidence=0.85,
        reusable=True,
        tags=["urban", "heat"],
    )
    memory.store(structure)

    results = memory.semantic_search("Which factors create the urban heat island effect?", limit=1)
    assert results
    found, score = results[0]
    assert found.id == structure.id
    assert score >= 0.20


def test_semantic_threshold_rejects_unrelated_candidate(tmp_path):
    memory = CognitiveMemory(db_path=str(tmp_path / "memory.db"), semantic_threshold=0.70)
    memory.store(
        CognitiveStructure(
            concept="urban heat islands",
            question="What causes urban heat islands?",
            findings=["Heat retention by built surfaces."],
            confidence=0.9,
            reusable=True,
            tags=["urban", "heat"],
        )
    )
    results = memory.semantic_search("How does photosynthesis work?", limit=1)
    assert results == []
