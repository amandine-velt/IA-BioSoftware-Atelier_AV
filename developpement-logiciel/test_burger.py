import re
import io
import builtins
from pytest import approx
from pathlib import Path
from burger import (
    get_order_timestamp,
    get_bun,
    get_meat,
    get_sauce,
    get_cheese,
    calculate_burger_price,
    assemble_burger,
    save_burger,
    BURGER_COUNT,
)


# --- Fonctions non interactives ---


def test_get_order_timestamp_format():
    ts = get_order_timestamp()
    assert isinstance(ts, str)
    assert re.match(r"\d{4}-\d{2}-\d{2}", ts)


def test_calculate_burger_price_basic():
    ingredients = ["bun", "beef", "cheddar", "ketchup"]
    expected = round((2.0 + 5.0 + 1.0 + 0.3) * 1.1, 2)
    assert calculate_burger_price(ingredients) == approx(expected, abs=0.01)


def test_calculate_burger_price_unknown_ingredient():
    ingredients = ["unknown", "beef"]
    expected = round((0 + 5.0) * 1.1, 2)
    assert calculate_burger_price(ingredients) == approx(expected, abs=0.01)


# --- Fonctions interactives avec monkeypatch ---


def test_get_bun_known(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "bun")
    assert get_bun() == "bun"


def test_get_bun_unknown(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "brioche")
    assert get_bun() == "other"


def test_get_meat_known(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "duck")
    assert get_meat() == "duck"


def test_get_meat_unknown(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "dragon")
    assert get_meat() == "mystery_meat"


def test_get_cheese_known(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "cheddar")
    assert get_cheese() == "cheddar"


def test_get_cheese_unknown(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "cantal")
    assert get_cheese() == "mystery_cheese"


def test_get_sauce_multiple(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "ketchup, mustard")
    assert get_sauce() == ["ketchup", "mustard"]


def test_get_sauce_empty(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert get_sauce() == ["ketchup"]


# --- Test global d'assemblage ---


def test_assemble_burger(monkeypatch):
    inputs = iter(["bun", "beef", "ketchup", "cheddar"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    burger = assemble_burger()

    assert isinstance(burger, str)
    assert "bun bun" in burger
    assert "beef" in burger
    assert "ketchup" in burger
    assert "cheddar cheese" in burger
    assert "Total price:" in burger

# --- Test d’écriture fichier avec fichier temporaire ---
def test_save_burger_creates_files(tmp_path, monkeypatch):
    import tempfile
    import burger

    test_burger = "bun + beef + ketchup + cheddar cheese\nTotal price: 9.99 €"
    created_paths = {}

    class FakeNamedTempFile:
        def __init__(self, path):
            self._file = open(path, "w", encoding="utf-8")
            self.name = str(path)
            self._path = path

        def write(self, data):
            return self._file.write(data)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._file.close()

        def close(self):
            self._file.close()

        def flush(self):
            self._file.flush()

    def temp_file_mock(*args, **kwargs):
        prefix = kwargs.get("prefix", "")
        if "burger_count" in prefix:
            path = tmp_path / "burger_count.txt"
            created_paths["count"] = path
        else:
            path = tmp_path / "burger.txt"
            created_paths["burger"] = path
        return FakeNamedTempFile(path)

    # Patch NamedTemporaryFile
    monkeypatch.setattr(tempfile, "NamedTemporaryFile", temp_file_mock)

    # Forcer BURGER_COUNT = 1
    burger.BURGER_COUNT = 1

    # Appel de la fonction à tester
    burger.save_burger(test_burger)

    # Récupération des chemins simulés
    burger_file = created_paths["burger"]
    count_file = created_paths["count"]

    # Vérifications
    assert burger_file.exists(), "Le fichier burger.txt n’a pas été créé"
    assert count_file.exists(), "Le fichier burger_count.txt n’a pas été créé"
    assert "cheddar cheese" in burger_file.read_text()
    assert int(count_file.read_text()) == 1

def test_main(monkeypatch, caplog):
    inputs = iter(["bun", "beef", "ketchup", "cheddar"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    from burger import main

    with caplog.at_level("INFO"):
        main()

    logs = "\n".join(caplog.messages)
    assert "Total price" in logs

