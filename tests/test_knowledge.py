from anne_core.knowledge import ANNEIdentity, KnowledgeManifest, PrivateVault


def test_identity_is_stable(tmp_path):
    path = tmp_path / "anne_id"
    first = ANNEIdentity.load_or_create(path)
    second = ANNEIdentity.load_or_create(path)
    assert first == second
    assert first.anne_id.startswith("ANNE-")


def test_private_vault_round_trip_and_wrong_password(tmp_path):
    source = b"private institutional knowledge"
    blob = PrivateVault.encrypt(source, "a strong local passphrase")
    assert PrivateVault.decrypt(blob, "a strong local passphrase") == source

    try:
        PrivateVault.decrypt(blob, "wrong password")
    except Exception:
        pass
    else:
        raise AssertionError("wrong passphrase must not decrypt the vault")


def test_manifest_is_content_addressed_and_consent_aware():
    identity = ANNEIdentity.create()
    manifest = KnowledgeManifest.from_content(
        b"validated result",
        "example research",
        identity.anne_id,
        license="cc-by-4.0",
        share_scope="anonymous-network",
        confidence=0.9,
        provenance=["MITOS:test", "source:test"],
    )
    restored = KnowledgeManifest.from_json(manifest.to_json())
    assert restored == manifest
    assert restored.content_hash.startswith("sha256:")
    assert restored.share_scope == "anonymous-network"
    assert restored.owner_anne_id == identity.anne_id
