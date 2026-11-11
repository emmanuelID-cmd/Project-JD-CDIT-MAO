"""Default synthetic data paths work when the app starts outside the project root."""
from cdit_support_mao.agents.knowledge.corpus import default_knowledge_dir, load_corpus
from cdit_support_mao.agents.troubleshooting.policy import default_policy_path, load_policy


def test_default_paths_resolve_from_any_start_folder(tmp_path, monkeypatch):
    monkeypatch.delenv("CDIT_KNOWLEDGE_DIR", raising=False)
    monkeypatch.delenv("CDIT_TROUBLESHOOTING_POLICY", raising=False)
    monkeypatch.chdir(tmp_path)
    assert default_knowledge_dir().is_dir()
    assert default_policy_path().is_file()
    assert load_corpus().articles
    assert load_policy().version


def test_relative_path_present_in_start_folder_is_kept(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "local-kb").mkdir()
    monkeypatch.setenv("CDIT_KNOWLEDGE_DIR", "local-kb")
    assert str(default_knowledge_dir()) == "local-kb"
