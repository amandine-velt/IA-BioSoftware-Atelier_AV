import pytest
import re
import os
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

# --- Test fonctions non interactives ---


def test_get_order_timestamp_format():
    ts = get_order_timestamp()
    assert isinstance(ts, str)
    assert re.match(r"\d{4}-\d{2}-\d{2}", ts)


def test_calculate_burger_price_basic():
    ingredients = ["bun", "beef", "cheddar", "ketchup"]
    expected = round((2.0 + 5.0 + 1.0 + 0.3) * 1.1, 2)  # 10% tax
    assert calculate_burger_price(ingredients) == expected


def test_calculate_burger_price_unknown_ingredient():
    ingredients = ["unknown", "beef"]
    expected = round((0 + 5.0) * 1.1, 2)
    assert calculate_burger_price(ingredients) == expected


# --- Test fonctions interactives avec monkeypatch ---


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


def test_assemble_burger(monkeypatch):
    # Simuler toutes les entrées utilisateur
    inputs = iter(
        [
            "bun",  # bun
            "beef",  # meat
            "ketchup",  # sauce
            "cheddar",  # cheese
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    burger = assemble_burger()

    assert isinstance(burger, str)
    assert "bun bun" in burger
    assert "beef" in burger
    assert "ketchup" in burger
    assert "cheddar cheese" in burger
    assert "Total price:" in burger


def test_save_burger(tmp_path, monkeypatch):
    test_burger = "test bun + test meat + test sauce + test cheese\nTotal price: 9.99 €"

    tmp_burger_file = tmp_path / "burger.txt"
    tmp_count_file = tmp_path / "burger_count.txt"

    # Capture l'open original
    import builtins

    real_open = builtins.open

    # Monkeypatch open() pour rediriger vers les fichiers temporaires
    def custom_open(file, mode="r", *args, **kwargs):
        if file == "/tmp/burger.txt":
            return real_open(tmp_burger_file, mode, *args, **kwargs)
        elif file == "/tmp/burger_count.txt":
            return real_open(tmp_count_file, mode, *args, **kwargs)
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", custom_open)

    # Appel réel
    from burger import save_burger, BURGER_COUNT

    save_burger(test_burger)

    # Vérification du contenu
    with tmp_burger_file.open() as f:
        assert "test cheese" in f.read()

    with tmp_count_file.open() as f:
        assert int(f.read()) == BURGER_COUNT
