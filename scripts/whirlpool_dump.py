#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "whirlpool-sixth-sense==1.0.3",
#     "aiohttp",
# ]
# ///
"""
Dump every Whirlpool appliance on your account, with its data-model key and the
full attribute map (name = current value).

Run with uv (no venv needed):
    uv run whirlpool_dump.py
or, after `chmod +x`:
    ./whirlpool_dump.py

Credentials (in priority order):
    env WHIRLPOOL_EMAIL / WHIRLPOOL_PASSWORD, else interactive prompt.
Optional overrides:
    WHIRLPOOL_REGION  (US | EU,  default US)
    WHIRLPOOL_BRAND   (Whirlpool | Maytag | KitchenAid | Consul, default Whirlpool)

Recon workflow for the hood light/fan:
    1. Run once, save the output.
    2. Cycle Hood Light through Off -> Low -> High in the Whirlpool app.
    3. Run again and diff. The attribute whose value tracks the level is your key.
       (Expect a multi-value int like 0/1/2, not a 0/1 bool.)
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

        locations = data.get(str(acct), {})
        if not locations:
            print("No owned appliances returned for this account.")
            return

        for loc in locations.values():
            for a in loc:
                print("=" * 72)
                print(
                    f'{a["APPLIANCE_NAME"]} | {a["CATEGORY_NAME"]} '
                    f'| {a["DATA_MODEL_KEY"]} | SAID={a["SAID"]}'
                )
                print("-" * 72)

                info = ApplianceInfo(
                    said=a["SAID"],
                    name=a["APPLIANCE_NAME"],
                    data_model=a["DATA_MODEL_KEY"],
                    category=a["CATEGORY_NAME"],
                    model_number=a.get("MODEL_NO", ""),
                    serial_number=a.get("SERIAL", ""),
                )

                app = Appliance(bs, auth, session, info)
                if not await app.fetch_data():
                    print("  (failed to fetch attribute data)")
                    continue

                # _data_dict is the raw fetched payload; attributes live under "attributes".
                attributes = app._data_dict.get("attributes", {})
                if not attributes:
                    print("  (no attributes present)")
                    continue
                for k in sorted(attributes):
                    print(f'  {k} = {attributes[k].get("value")}')

        print("=" * 72)


if __name__ == "__main__":
    asyncio.run(main())
