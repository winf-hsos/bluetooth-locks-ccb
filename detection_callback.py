import asyncio
import logging
import sys

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

logger = logging.getLogger(__name__)


def simple_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    if(device.name == "PSLOCK"):
        #logger.info(f"{device.name}: {device.address}: {advertisement_data}")
        logger.info(advertisement_data.manufacturer_data)

        adv_bytes = advertisement_data.manufacturer_data.get(65535)
        logger.info(list(adv_bytes))
        #logger.info(f"Number of bytes: { len(list(adv_bytes)) }")
        logger.info(f"Battery level: {list(adv_bytes)[0]} %")
        logger.info(f"Lock state: {list(adv_bytes)[3]}")
        logger.info(f"Door state: {list(adv_bytes)[4]}")
        logger.info(f"Open time: {list(adv_bytes)[6]}")


async def main(service_uuids):
    scanner = BleakScanner(simple_callback, service_uuids)

    while True:
        logger.info("(re)starting scanner")
        await scanner.start()
        await asyncio.sleep(60.0)
        await scanner.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )
    service_uuids = sys.argv[1:]
    asyncio.run(main(service_uuids))