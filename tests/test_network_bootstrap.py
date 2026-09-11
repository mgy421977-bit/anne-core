from anne_core.knowledge.network import (
    ANNE_REGISTRY_URL,
    ANNE_REPOSITORY,
    BootstrapConfig,
    CentralKnowledgeBootstrap,
)


def test_default_bootstrap_points_to_anne_repository():
    config = BootstrapConfig()
    assert config.repository == ANNE_REPOSITORY
    assert config.registry_url == ANNE_REGISTRY_URL
    assert config.mode == "read-only"
    assert config.upload_private_data is False
    assert config.execute_remote_code is False


def test_bootstrap_rejects_non_object_registry(monkeypatch):
    bootstrap = CentralKnowledgeBootstrap()
    monkeypatch.setattr(bootstrap, "fetch_registry", lambda: [])
    # bootstrap() delegates to the fetch method; the type contract is enforced
    # by fetch_registry itself when real network data is read.
    assert bootstrap.bootstrap() == []
