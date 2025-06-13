import os
import time
import logging
from datetime import datetime

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
    return str(datetime.now())


def get_bun():
    bun_type = input("What kind of bun would you like? ").strip().lower()

    if bun_type != "bun":
        logging.info(f"Unknown bun type '{bun_type}' — using default: other")
        bun_type = "other"
    else:
        logging.info(f"Selected bun: {bun_type}")

    return bun_type


def calculate_burger_price(ingredients_list):
    def add_tax(price, tax_rate=0.1, times=1):
        for _ in range(times):
            price += price * tax_rate
        return price

    base_price = 0
    for ingredient in ingredients_list:
        ingredient = ingredient.strip().lower()
        price = INGREDIENT_PRICES.get(ingredient, 0)
        if debug:
            logging.info(f"Ingredient: {ingredient}, Price: {price}")
        base_price += price

    final_price = add_tax(base_price)
    return round(final_price, 2)


def get_meat():
    allowed_meats = ["beef", "tofu", "duck", "fish", "chicken"]
    meat_type = input("Enter the meat type: ").strip().lower()

    if meat_type not in allowed_meats:
        logging.info(f"Unknown meat '{meat_type}' — using default: mystery_meat")
        meat = "mystery_meat"
    else:
        meat = meat_type

    logging.info(f"Selected meat: {meat}")
    return meat


def get_sauce():
    available_sauces = ["ketchup", "mustard", "mayonnaise", "barbecue"]
    logging.info("Available sauces: " + ", ".join(available_sauces))

    selected = input("Choose your sauces (separate by commas): ").strip()
    sauce_list = [s.strip().lower() for s in selected.split(",") if s.strip()]

    if not sauce_list:
        logging.info("No valid sauce selected. Defaulting to ketchup.")
        sauce_list = ["ketchup"]

    logging.info(f"Selected sauce(s): {', '.join(sauce_list)}")
    return sauce_list


def get_cheese():
    available_cheeses = ["cheddar", "emmental", "mozzarella", "blue cheese", "goat cheese"]
    logging.info("Available cheeses: " + ", ".join(available_cheeses))

    cheese_type = input("What kind of cheese? ").strip().lower()

    if cheese_type not in available_cheeses:
        logging.info(f"Unknown cheese '{cheese_type}' — using default: mystery_cheese")
        cheese = "mystery_cheese"
    else:
        cheese = cheese_type

    logging.info(f"Selected cheese: {cheese}")
    return cheese


def assemble_burger():
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
        logging.error(f"Error during burger assembly: {e}")
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
    try:
        with open("/tmp/burger.txt", "w") as f:
            f.write(burger)

        with open("/tmp/burger_count.txt", "w") as f:
            f.write(str(BURGER_COUNT))

        logging.info("Burger saved to /tmp/burger.txt")
    except Exception as e:
        logging.error(f"Error saving burger: {e}")


def main():
    logging.info("Welcome to the worst burger maker ever!")

    try:
        burger = assemble_burger()
        if burger:
            save_burger(burger)
            logging.info(f"Final burger composition/price : {burger}")
        else:
            logging.info("Burger assembly failed.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
