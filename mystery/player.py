from animation import Animation, Direction
from params import Params
from utils import Point2D


class Player:
    def __init__(self, params: Params, pos: Point2D, animation: Animation):
        self.params = params
        self.pos = pos
        self.speed = 0.25
        self.dx = 0
        self.dy = 0
        self.animation = animation

    def move(self, room):
        new_pos = Point2D(self.pos.x + self.dx * self.speed, self.pos.y + self.dy * self.speed)

        if not (self.collides_with_terrain(new_pos, room.terrain) or self.collides_with_npcs(new_pos, room.npcs)):
            self.pos = new_pos

        for door in room.doors:
            if self.collides_with_door(new_pos, door):
                return door.out_room

        return room.name

    def draw(self, screen):
        if self.dx < 0:
            direction = Direction.LEFT
        elif self.dx > 0:
            direction = Direction.RIGHT
        else:
            direction = None
        self.animation.draw(screen=screen, pos=self.pos, direction=direction)

    def collides_with_terrain(self, pos, terrain):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < terrain.shape[1] and 0 <= y < terrain.shape[0]:
            return terrain[y, x]
        return False

    def collides_with_npcs(self, pos, npcs):
        for npc in npcs:
            if self.collides_with_single_npc(pos, npc):
                return True
        return False

    def collides_with_single_npc(self, pos, npc):
        distance = ((pos.x - npc.pos.x) ** 2 + (pos.y - npc.pos.y) ** 2) ** 0.5
        return distance <= self.params.NPC_RADIUS

    def collides_with_door(self, pos, door):
        return (
            door.rectangle.top_left.x <= pos.x <= door.rectangle.top_left.x + door.rectangle.width
            and door.rectangle.top_left.y <= pos.y <= door.rectangle.top_left.y + door.rectangle.height
        )
