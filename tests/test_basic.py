def test_import():
    import termcap
    assert termcap
    assert termcap.__version__ == "0.2.2"

def test_config():
    from termcap.config import get_config_manager
    manager = get_config_manager()
    config = manager.load_config()
    assert config
