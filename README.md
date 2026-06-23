# ha-whirlpool-microwave

Home Assistant support for the Whirlpool over-the-range microwave-hood combo: the hood light and exhaust fan, plus the microwave's controllable surface. Whirlpool's official HA integration covers no `Cooking`-category appliances, so this fills the gap until it lands upstream.

The cloud protocol is reverse-engineered and confirmed against real hardware (see `scripts/`); the integration exposes the hood light, exhaust fan, switches, and status sensors, and is validated end to end against a real device.

## Device

Developed on a Whirlpool `WMH78019HZ` over-the-range microwave (data model `DDM_COOKING_MHC76_V1`, category `Cooking`). Other Whirlpool / Maytag / KitchenAid microwave-hood combos on the same data model should work.

## What it controls

| Control | Cloud attribute | Values |
|---|---|---|
| Hood light | `Hood_OperationSetSurfaceLight` | off=0, low=2, high=4 |
| Hood fan | `Hood_OperationSetExhaustFanSpeed` | off=0, low=2, medium=4, med-high=5, high=6 |
| Quiet mode | `Sys_OperationSetQuietModeEnabled` | 0/1 |
| Control lock | `Sys_OperationSetControlLock` | 0/1 |
| Turntable | `Mwo_CycleSetTurntable` | 0/1 |

Read-only status: door open (`Mwo_OperationStatusDoorOpen`), running (`Mwo_ModeStatusIdle`, inverted), cook-time remaining (`Mwo_TimeStatusCookTimeRemaining`).

## Install (HACS)

Install in Home Assistant via HACS as a custom repository:

HACS → three-dot menu → Custom repositories → add `https://github.com/clintval/ha-whirlpool-microwave` as an Integration → install → restart HA → Settings → Devices & Services → Add Integration → "Whirlpool Microwave".

## scripts/

Standalone [`uv`](https://docs.astral.sh/uv/) scripts used to reverse-engineer and verify the protocol. Credentials come from `WHIRLPOOL_EMAIL` / `WHIRLPOOL_PASSWORD` env vars or an interactive prompt; nothing is hardcoded.

- `whirlpool_dump.py`: dump every appliance on the account with its full attribute map. Run before and after toggling a control in the Whirlpool app, then diff to find the attribute key.
- `whirlpool_write_test.py`: cycle the hood light Off → Low → High → Off via `send_attributes`, reading each value back, to confirm writes are accepted. Set `TEST_FAN=1` to also cycle the fan.

Built on [`whirlpool-sixth-sense`](https://github.com/abmantis/whirlpool-sixth-sense).

## License

MIT
