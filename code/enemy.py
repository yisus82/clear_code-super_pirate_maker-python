from sprites import Animated


class Enemy(Animated):
    def __init__(
        self,
        enemy_type,
        position,
        groups,
        animations,
        status="idle",
        pivot="bottomleft",
    ):
        super().__init__(position, animations, groups, status, pivot)
        self.enemy_type = enemy_type
