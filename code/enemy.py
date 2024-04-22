from sprites import Animated


class Enemy(Animated):
    def __init__(self, enemy_type, position, groups, animations, status="idle"):
        super().__init__(position, animations, groups, status, bottom=True)
        self.enemy_type = enemy_type
