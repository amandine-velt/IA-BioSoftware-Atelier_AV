import os
import time
import logging
from datetime import datetime
import tempfile

# Logger personnalisé
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BURGER_COUNT = 0
last_burger = None
debug = True

INGREDIENT_PRICES = {
    "bun": 2.0,
    "other": 2.5,
    "beef": 5.0,
    "mystery meat": 3.5,
    "tofu": 3.0,
    "duck": 5.5,
    "fish": 4.5,
    "chicken": 4.0,
    "mystery_cheese": 1.5,
    "cheddar": 1.0,
    "emmental": 1.0,
    "mozzarella": 1.0,
    "blue cheese": 1.0,
    "goat cheese": 1.0,
    "tomato": 0.5,
    "lettuce": 0.5,
    "ketchup": 0.3,
    "mustard": 0.3,
    "mayonnaise": 0.3,
    "barbecue": 0.3,
}


def get_order_timestamp():
    """Retourne un timestamp de commande formaté."""
    return str(datetime.now())


def get_bun():
    """Demande à l'utilisateur le type de pain et le valide."""
    bun_type = input("What kind of bun would you like? ").strip().lower()

    if bun_type != "bun":
        logger.info("Unknown bun type '%s' — using default: other", bun_type)
        bun_type = "other"
    else:
        logger.info("Selected bun: %s", bun_type)

    return bun_type


def calculate_burger_price(ingredients_list):
    """Calcule le prix final du burger avec taxes à partir des ingrédients."""
    def add_tax(price, tax_rate=0.1, times=1):
        for _ in range(times):
            price += price * tax_rate
        return price

    base_price = 0
    for ingredient in ingredients_list:
        ingredient = ingredient.strip().lower()
        price = INGREDIENT_PRICES.get(ingredient, 0)
        if debug:
            logger.info("Ingredient: %s, Price: %s", ingredient, price)
        base_price += price

    final_price = add_tax(base_price)
    return round(final_price, 2)


def get_meat():
    """Demande le type de viande et applique une valeur par défaut si nécessaire."""
    allowed_meats = ["beef", "tofu", "duck", "fish", "chicken"]
    meat_type = input("Enter the meat type: ").strip().lower()

    if meat_type not in allowed_meats:
        logger.info("Unknown meat '%s' — using default: mystery_meat", meat_type)
        meat = "mystery_meat"
    else:
        meat = meat_type

    logger.info("Selected meat: %s", meat)
    return meat


def get_sauce():
    """Demande les sauces et retourne une liste."""
    available_sauces = ["ketchup", "mustard", "mayonnaise", "barbecue"]
    logger.info("Available sauces: %s", ", ".join(available_sauces))

    selected = input("Choose your sauces (separate by commas): ").strip()
    sauce_list = [s.strip().lower() for s in selected.split(",") if s.strip()]

    if not sauce_list:
        logger.info("No valid sauce selected. Defaulting to ketchup.")
        sauce_list = ["ketchup"]

    logger.info("Selected sauce(s): %s", ", ".join(sauce_list))
    return sauce_list


def get_cheese():
    """Demande le type de fromage et applique une valeur par défaut si nécessaire."""
    available_cheeses = [
        "cheddar",
        "emmental",
        "mozzarella",
        "blue cheese",
        "goat cheese",
    ]
    logger.info("Available cheeses: %s", ", ".join(available_cheeses))

    cheese_type = input("What kind of cheese? ").strip().lower()

    if cheese_type not in available_cheeses:
        logger.info("Unknown cheese '%s' — using default: mystery_cheese", cheese_type)
        cheese = "mystery_cheese"
    else:
        cheese = cheese_type

    logger.info("Selected cheese: %s", cheese)
    return cheese


def assemble_burger():
    """Assemble les ingrédients saisis pour créer un burger."""
    global BURGER_COUNT, last_burger

    BURGER_COUNT += 1

    try:
        bun = get_bun()
        meat = get_meat()
        sauce_list = get_sauce()
        cheese = get_cheese()

        ingredients = [bun, meat, cheese] + sauce_list

        burger_data = {
            "bun": bun,
            "meat": meat,
            "sauce": " and ".join(sauce_list),
            "cheese": cheese,
            "id": BURGER_COUNT,
            "price": calculate_burger_price(ingredients),
            "timestamp": get_order_timestamp(),
        }

    except Exception as e:
        logger.error("Error during burger assembly: %s", e)
        return None

    burger = (
        f"{burger_data['bun']} bun + "
        f"{burger_data['meat']} + "
        f"{burger_data['sauce']} + "
        f"{burger_data['cheese']} cheese\n"
        f"Total price: {burger_data['price']} €"
    )

    last_burger = burger
    return burger


def save_burger(burger):
    """Sauvegarde un burger et son compteur dans des fichiers temporaires."""
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, prefix="burger_", suffix=".txt") as f:
            f.write(burger)
            burger_path = f.name

        with tempfile.NamedTemporaryFile("w", delete=False, prefix="burger_count_", suffix=".txt") as f:
            f.write(str(BURGER_COUNT))
            count_path = f.name

        logger.info("Burger saved to %s", burger_path)
        logger.info("Burger count saved to %s", count_path)
    except Exception as e:
        logger.error("Error saving burger: %s", e)


def main():
    """Fonction principale pour lancer l'assemblage et la sauvegarde du burger."""
    logger.info("Welcome to the worst burger maker ever!")

    try:
        burger = assemble_burger()
        if burger:
            save_burger(burger)
            logger.info("Final burger composition/price : %s", burger)
        else:
            logger.info("Burger assembly failed.")
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)


if __name__ == "__main__":
    main()
