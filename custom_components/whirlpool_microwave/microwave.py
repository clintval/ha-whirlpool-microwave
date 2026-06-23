"""Whirlpool over-the-range microwave-hood appliance."""
from __future__ import annotations

from whirlpool.appliance import Appliance

from . import const


class Microwave(Appliance):
    """Microwave-hood combo: hood light, exhaust fan, switches, status.

    Built on the base Appliance, which provides send_attributes, fetch_data,
    get_online, and the _get_attribute / _get_int_attribute / bool_to_attr_value
    / attr_value_to_bool helpers. All device values are strings on the wire.
    """

    def get_light_level(self) -> str | None:
        value = self._get_attribute(const.ATTR_LIGHT)
        return None if value is None else const.LIGHT_VALUE_TO_LEVEL.get(value)

    async def set_light_level(self, level: str) -> bool:
        if level not in const.LIGHT_LEVELS:
            raise ValueError(f"invalid hood light level: {level!r}")
        return await self.send_attributes({const.ATTR_LIGHT: const.LIGHT_LEVELS[level]})

    def get_fan_speed(self) -> str | None:
        value = self._get_attribute(const.ATTR_FAN)
        return None if value is None else const.FAN_VALUE_TO_SPEED.get(value)

    async def set_fan_speed(self, speed: str) -> bool:
        if speed not in const.FAN_SPEEDS:
            raise ValueError(f"invalid hood fan speed: {speed!r}")
        return await self.send_attributes({const.ATTR_FAN: const.FAN_SPEEDS[speed]})

    def get_quiet_mode(self) -> bool | None:
        return self.attr_value_to_bool(self._get_attribute(const.ATTR_QUIET))

    async def set_quiet_mode(self, on: bool) -> bool:
        return await self.send_attributes({const.ATTR_QUIET: self.bool_to_attr_value(on)})

    def get_control_lock(self) -> bool | None:
        return self.attr_value_to_bool(self._get_attribute(const.ATTR_LOCK))

    async def set_control_lock(self, on: bool) -> bool:
        return await self.send_attributes({const.ATTR_LOCK: self.bool_to_attr_value(on)})

    def get_turntable(self) -> bool | None:
        return self.attr_value_to_bool(self._get_attribute(const.ATTR_TURNTABLE))

    async def set_turntable(self, on: bool) -> bool:
        return await self.send_attributes({const.ATTR_TURNTABLE: self.bool_to_attr_value(on)})

    def get_door_open(self) -> bool | None:
        return self.attr_value_to_bool(self._get_attribute(const.ATTR_DOOR))

    def get_running(self) -> bool | None:
        idle = self.attr_value_to_bool(self._get_attribute(const.ATTR_IDLE))
        return None if idle is None else not idle

    def get_cook_time_remaining(self) -> int | None:
        return self._get_int_attribute(const.ATTR_COOK_REMAINING)
