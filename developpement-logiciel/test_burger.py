import re
import builtins
from pytest import approx
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
    test_burger = "bun + beef + ketchup + cheddar cheese\nTotal price: 9.99 €"

    # Monkeypatch NamedTemporaryFile pour écrire dans tmp_path
    def temp_file_mock(*args, **kwargs):
        suffix = kwargs.get("suffix", "")
        name = "burger.txt" if "burger" in suffix else "burger_count.txt"
        file_path = tmp_path / name
        f = file_path.open("w+")
        f.name = str(file_path)  # besoin de ce champ pour le logging
        return f

    monkeypatch.setattr("tempfile.NamedTemporaryFile", temp_file_mock)

    save_burger(test_burger)

    burger_file = tmp_path / "burger.txt"
    count_file = tmp_path / "burger_count.txt"

    assert burger_file.exists()
    assert count_file.exists()

    assert "cheddar" in burger_file.read_text()
    assert str(BURGER_COUNT) in count_file.read_text()

def test_main(monkeypatch, capsys):
    inputs = iter(["bun", "beef", "ketchup", "cheddar"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Import tardif du main pour éviter l’exécution au moment de l'import global
    from burger import main

    main()

    captured = capsys.readouterr()
    assert "Burger summary" in captured.out or "Total price" in captured.out
