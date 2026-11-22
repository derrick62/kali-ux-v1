from kali_ux.features.launcher import service as launcher_service


def test_launcher_discovers_desktop_metadata_and_searches_categories(monkeypatch, tmp_path):
    root = tmp_path / ".local/share/applications"
    root.mkdir(parents=True)
    (root / "sample.desktop").write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Sample Editor\n"
        "Comment=Edit source files\n"
        "Exec=sample-editor %F\n"
        "Icon=accessories-text-editor\n"
        "Categories=Development;TextEditor;\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(launcher_service.Path, "home", lambda: tmp_path)
    launcher = launcher_service.ApplicationLauncher()
    result = launcher.search("development")
    assert len(result) == 1
    assert result[0].name == "Sample Editor"
    assert result[0].icon == "accessories-text-editor"
    assert result[0].description == "Edit source files"


def test_launcher_skips_hidden_desktop_entries(monkeypatch, tmp_path):
    root = tmp_path / ".local/share/applications"
    root.mkdir(parents=True)
    (root / "hidden.desktop").write_text(
        "[Desktop Entry]\nType=Application\nName=Hidden\nExec=hidden\nHidden=true\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(launcher_service.Path, "home", lambda: tmp_path)
    launcher = launcher_service.ApplicationLauncher()
    assert all(entry.name != "Hidden" for entry in launcher.entries)
