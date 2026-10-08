from anne_core.runtime import ANNERuntime, AdapterRegistry, inspect_environment


def test_environment_discovery_is_dependency_light():
    env = inspect_environment()
    assert env.cpu_count > 0
    assert env.os_name
    assert env.architecture
    assert env.python_version


def test_runtime_bootstrap_selects_cpu_fallback_when_no_gpu(monkeypatch):
    from anne_core.runtime import environment
    monkeypatch.setattr(environment, "_accelerators", lambda: ())
    runtime = ANNERuntime(AdapterRegistry())
    status = runtime.bootstrap()
    assert status.operational
    assert any(a.name == "cpu-fallback" for a in status.adapters)
    assert status.environment.accelerators == ()


def test_runtime_does_not_auto_install_external_adapters():
    runtime = ANNERuntime()
    status = runtime.bootstrap()
    for plan in status.missing_optional_adapters:
        assert plan.requires_approval is True
        assert plan.status == "not-installed"


def test_runtime_recovery_re_discovers_environment():
    runtime = ANNERuntime()
    first = runtime.bootstrap()
    second = runtime.recover()
    assert second.environment.os_name == first.environment.os_name
    assert second.environment.architecture == first.environment.architecture
