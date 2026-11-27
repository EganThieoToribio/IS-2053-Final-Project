import random

ROCK = 1
PAPER = 2
SCISSORS = 3

MOVE_NAMES = {
    ROCK: "Rock",
    PAPER: "Paper",
    SCISSORS: "Scissors",
}


def choice_name(choice: int) -> str:
    """Convert a numeric RPS choice (1-3) into a readable move name."""
    return MOVE_NAMES.get(choice, "Unknown")


class Player:
    def __init__(
        self,
        name: str,
        max_health: int,
        money: int,
        min_damage: int,
        max_damage: int,
    ):
        self.name = name
        self.max_health = max(1, max_health)
        self.health = self.max_health
        self.min_damage = max(0, min_damage)
        self.max_damage = max(self.min_damage, max_damage)
        self.money = max(0, money)
        self.has_weighted_rock = False
        self.has_paper_armor = False
        self.has_sharpened_scissors = False
        self.has_crown = False

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, dmg: int):
        if dmg > 0:
            self.health -= dmg
            if self.health < 0:
                self.health = 0

    def refill_health(self):
        self.health = self.max_health

    def pay_gold(self, price: int) -> bool:
        """Deduct gold if affordable; returns True if payment succeeded."""
        if price < 0:
            return False
        if self.money >= price:
            self.money -= price
            return True
        return False

    def update_min_dmg(self, bonus: int):
        self.min_damage += bonus
        if self.min_damage < 0:
            self.min_damage = 0
        if self.max_damage < self.min_damage:
            self.max_damage = self.min_damage

    def update_max_dmg(self, bonus: int):
        self.max_damage += bonus
        if self.max_damage < self.min_damage:
            self.max_damage = self.min_damage

    def update_max_health(self, bonus: int):
        self.max_health += bonus
        if self.max_health < 1:
            self.max_health = 1
        if bonus > 0:
            self.health += bonus
        elif self.health > self.max_health:
            self.health = self.max_health

    def roll_damage(self) -> int:
        """Roll base damage between min_damage and max_damage."""
        if self.max_damage <= self.min_damage:
            return self.min_damage
        return random.randint(self.min_damage, self.max_damage)

    def calculate_attack_damage(self, move_choice: int | None = None, won_round: bool = False) -> int:
        """
        Calculate outgoing damage using base roll and owned items.
        - Weighted Rock: +3 bonus damage when playing Rock (or winning with Rock).
        - Sharpened Scissors: +3 bonus damage when playing Scissors (or winning with Scissors).
        - Crown: +2 flat bonus damage on attacks.
        """
        dmg = self.roll_damage()

        if move_choice == ROCK and self.has_weighted_rock:
            dmg += 3
        elif move_choice == SCISSORS and self.has_sharpened_scissors:
            dmg += 3

        if self.has_crown:
            dmg += 2

        return dmg

    def calculate_damage_taken(self, incoming_dmg: int, move_choice: int | None = None) -> int:
        """
        Calculate damage actually taken after item mitigation.
        - Paper Armor: reduces incoming damage by 2 (minimum 1 if incoming_dmg > 0).
        """
        if incoming_dmg <= 0:
            return 0

        reduced = incoming_dmg
        if self.has_paper_armor:
            reduced -= 2

        if reduced < 1:
            return 1
        return reduced


class Enemy:
    def __init__(
        self,
        name: str,
        health: int,
        min_damage: int,
        max_damage: int,
    ):
        self.name = name
        self.max_health = max(1, health)
        self.health = self.max_health
        self.min_damage = max(0, min_damage)
        self.max_damage = max(self.min_damage, max_damage)

    def is_alive(self) -> bool:
        return self.health > 0

    def rps_choice(self) -> int:
        return random.randint(ROCK, SCISSORS)

    def rps_choice_name(self, choice: int) -> str:
        return choice_name(choice)

    def roll_damage(self) -> int:
        if self.max_damage <= self.min_damage:
            return self.min_damage
        return random.randint(self.min_damage, self.max_damage)

    def take_damage(self, dmg: int):
        if dmg > 0:
            self.health -= dmg
            if self.health < 0:
                self.health = 0


if __name__ == "__main__":
    p = Player("Hero", max_health=30, money=25, min_damage=4, max_damage=7)
    e = Enemy("Goblin", health=20, min_damage=3, max_damage=6)

    p.has_weighted_rock = True
    p.has_paper_armor = True

    enemy_move = e.rps_choice()
    atk = p.calculate_attack_damage(move_choice=ROCK)
    e.take_damage(atk)

    incoming = p.calculate_damage_taken(e.roll_damage(), move_choice=ROCK)
    p.take_damage(incoming)

    print(f"{p.name} used Rock ({atk} dmg) vs {e.name}'s {choice_name(enemy_move)} -> Enemy HP: {e.health}/{e.max_health}")
    print(f"{e.name} hit {p.name} for {incoming} -> Player HP: {p.health}/{p.max_health}, Gold: {p.money}")