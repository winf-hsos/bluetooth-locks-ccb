import asyncio

from bleak import BleakScanner


async def main():
    time_out = 60
    print(f"scanning for {time_out} seconds, please wait...")

    devices = await BleakScanner.discover(return_adv=True, timeout=time_out)

    for d, a in devices.values():
        print()
        print(d)
        print("-" * len(str(d)))
        print(a)


if __name__ == "__main__":
    asyncio.run(main())