#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "whirlpool-sixth-sense==1.0.3",
#     "aiohttp",
# ]
# ///
"""
Write test for the Whirlpool over-the-range microwave hood (WMH78019HZ /
data model DDM_COOKING_MHC76_V1).

Proves the cloud accepts attribute WRITES (not just reads) by cycling the
hood surface light Off -> Low -> High -> Off, reading the value back after
each command, and restoring the original level at the end.

This is the companion to the read/dump script. Same auth, same Appliance
object; the only new call is Appliance.send_attributes({attr: value}), which
POSTs {"header": {"said", "command": "setAttributes"}, "body": {attr: value}}
and returns True on HTTP 200. Attribute values go over the wire as STRINGS.

Credentials (priority order):
    env WHIRLPOOL_EMAIL / WHIRLPOOL_PASSWORD, else interactive prompt.
Optional overrides:
    WHIRLPOOL_REGION  (US | EU, default US)
    WHIRLPOOL_BRAND   (Whirlpool | Maytag | KitchenAid | Consul, default Whirlpool)
    WHIRLPOOL_SAID    (target a specific appliance; default = first "Cooking")
    TEST_FAN=1        (also cycle the exhaust fan Off->Low->High->Off; it is LOUD)

Run with uv (no venv needed):
    uv run whirlpool_write_test.py
or, after `chmod +x`:
    ./whirlpool_write_test.py
"""

import asyncio
import os
import sys
from getpass import getpass

import aiohttp
from whirlpool.appliance import Appliance
from whirlpool.auth import Auth
from whirlpool.backendselector import Brand, BackendSelector, Region
from whirlpool.types import ApplianceInfo

LIGHT_ATTR = "Hood_OperationSetSurfaceLight"
LIGHT_STEPS = [("low", "2"), ("high", "4"), ("off", "0")]  # observed: off=0 low=2 high=4

FAN_ATTR = "Hood_OperationSetExhaustFanSpeed"
FAN_STEPS = [("low", "2"), ("high", "6"), ("off", "0")]  # observed: off=0 low=2 med=4 medhi=5 high=6

SETTLE_SECONDS = 5  # cloud round-trip + device action before we read back


def _creds() -> tuple[str, str]:
    email = os.environ.get("WHIRLPOOL_EMAIL") or input("Whirlpool email: ").strip()
    password = os.environ.get("WHIRLPOOL_PASSWORD") or getpass("Whirlpool password: ")
    if not email or not password:
        sys.exit("error: email and password are required")
    return email, password


def _backend() -> BackendSelector:
    region = getattr(Region, os.environ.get("WHIRLPOOL_REGION", "US"), Region.US)
    brand = getattr(Brand, os.environ.get("WHIRLPOOL_BRAND", "Whirlpool"), Brand.Whirlpool)
    return BackendSelector(brand, region)


def _read(app: Appliance, attr: str) -> str | None:
    """Read an attribute value straight from the last-fetched payload."""
    return app._data_dict.get("attributes", {}).get(attr, {}).get("value")


def _pick_appliance(locations: dict) -> dict:
    """Choose the target appliance: explicit SAID, else first Cooking, else first COOKING data model."""
    want_said = os.environ.get("WHIRLPOOL_SAID")
    appliances = [a for loc in locations.values() for a in loc]
    if not appliances:
        sys.exit("error: no owned appliances on this account")
    if want_said:
        for a in appliances:
            if a["SAID"] == want_said:
                return a
        sys.exit(f"error: no appliance with SAID={want_said}")
    for a in appliances:
        if a.get("CATEGORY_NAME") == "Cooking":
            return a
    for a in appliances:
        if "COOKING" in (a.get("DATA_MODEL_KEY") or "").upper():
            return a
    sys.exit("error: no Cooking appliance found; set WHIRLPOOL_SAID to target one explicitly")


async def _set_and_verify(app: Appliance, attr: str, name: str, value: str) -> None:
    print(f"  -> set {name:>4} ({attr}={value}) ...", end=" ", flush=True)
    ok = await app.send_attributes({attr: value})
    if not ok:
        print("REJECTED (send_attributes returned False -- cloud refused the write)")
        return
    print("accepted (HTTP 200)")
    await asyncio.sleep(SETTLE_SECONDS)
    await app.fetch_data()
    got = _read(app, attr)
    verdict = "OK" if got == value else "mismatch (not reflected yet?)"
    print(f"     read-back {attr} = {got}  [{verdict}]")


async def _cycle(app: Appliance, label: str, attr: str, steps: list[tuple[str, str]]) -> None:
    print(f"\n=== {label}: cycling {attr} -- WATCH THE APPLIANCE ===")
    original = _read(app, attr)
    print(f"  original {attr} = {original}")
    for name, value in steps:
        await _set_and_verify(app, attr, name, value)
    if original is not None:
        print(f"  restoring original {attr} = {original}")
        await app.send_attributes({attr: original})


async def main() -> None:
    email, password = _creds()
    bs = _backend()

    async with aiohttp.ClientSession() as session:
        auth = Auth(bs, email, password, session)
        await auth.do_auth(store=False)
        if not auth.is_access_token_valid():
            sys.exit("error: authentication failed (check credentials / region / brand)")

        acct = await auth.get_account_id()
        if not acct:
            sys.exit("error: could not resolve account id")

        async with session.get(
            bs.get_owned_appliances_url(acct), headers=auth.create_headers()
        ) as r:
            r.raise_for_status()
            data = await r.json()

        target = _pick_appliance(data.get(str(acct), {}))
        info = ApplianceInfo(
            said=target["SAID"],
            name=target["APPLIANCE_NAME"],
            data_model=target["DATA_MODEL_KEY"],
            category=target["CATEGORY_NAME"],
            model_number=target.get("MODEL_NO", ""),
            serial_number=target.get("SERIAL", ""),
        )
        print("=" * 72)
        print(f'Target: {info.name} | {info.category} | {info.data_model} | SAID={info.said}')
        print("=" * 72)

        app = Appliance(bs, auth, session, info)
        if not await app.fetch_data():
            sys.exit("error: could not fetch current appliance data")

        await _cycle(app, "HOOD LIGHT", LIGHT_ATTR, LIGHT_STEPS)

        if os.environ.get("TEST_FAN") == "1":
            await _cycle(app, "HOOD FAN (loud!)", FAN_ATTR, FAN_STEPS)
        else:
            print("\n(skipping fan test; set TEST_FAN=1 to also cycle the exhaust fan)")

        print("\nDone. If every step said 'accepted' and read-back matched, writes work.")


if __name__ == "__main__":
    asyncio.run(main())
