from door import Door
from room import Room

# TODO: Remove shapely requirement for polygon collision
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from utils import Point2D


def point_in_polygon(point: Point2D, polygon: list[float]):
    polygon = Polygon([p.to_tuple() for p in polygon])
    return polygon.contains(Point(point.x, point.y))


class Walker:
    def __init__(
        self,
        pos: Point2D,
        current_room: Room,
        rooms: list[Room],
        terrain_collision: bool = True,
        npc_collision: bool = True,
        door_collision: bool = True,
    ):
        self.pos = pos
        self.speed = 1.0
        self.dx = 0
        self.dy = 0
        self.rooms = rooms
        self.current_room = current_room

        self.terrain_collision = terrain_collision
        self.npc_collision = npc_collision
        self.door_collision = door_collision

    def _find_mirror_door(self, door: Door, room: Room):
        for out_door in room.doors:
            if out_door.in_room == door.out_room and out_door.out_room == door.in_room:
                return out_door
        raise ValueError("Mirror door not found")

    def move(self, room, npcs=None):
        self.d_pos = Point2D(self.dx, self.dy)
        new_pos = self.pos + self.d_pos * self.speed

        for door in room.doors:
            if self.collides_with_door(new_pos, door):
                self.current_room = self.rooms[door.out_room]
                # saloon
                out_door = self._find_mirror_door(door, self.current_room)
                self.pos = out_door.get_safe_exit_pos()
                self.current_room = self.rooms[door.out_room]
                return self.current_room.name

        if self.terrain_collision and self.collides_with_terrain(new_pos, room.terrain):
            # TODO? Do anything on terrain collision?
            pass
        elif self.npc_collision and self.collides_with_npcs(new_pos, npcs):
            # TODO? Do anything on npc collision?
            pass
        else:
            self.pos = new_pos

        return room.name

    def collides_with_terrain(self, pos, terrain):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < terrain.shape[1] and 0 <= y < terrain.shape[0]:
            return terrain[y, x]
        return False

    def collides_with_npcs(self, pos, npcs):
        assert npcs is not None
        for npc in npcs:
            if self.collides_with_single_npc(pos, npc):
                return True
        return False

    def collides_with_single_npc(self, pos, npc):
        distance = ((pos.x - npc.pos.x) ** 2 + (pos.y - npc.pos.y) ** 2) ** 0.5
        return distance <= self.params.NPC_RADIUS

    def collides_with_door(self, pos, door):
        if door.polygon is not None:
            return point_in_polygon(pos, door.polygon)
        elif door.pos is not None:
            return (
                door.rectangle.top_left.x <= pos.x <= door.rectangle.top_left.x + door.rectangle.width
                and door.rectangle.top_left.y <= pos.y <= door.rectangle.top_left.y + door.rectangle.height
            )
        else:
            raise ValueError("Door must have either pos or polygon")
