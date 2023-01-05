import asyncio
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

# Global variable to check whether status has been retrieved successfully
status_retrieved = False

async def _unlock(mac_address):

    try:
        async with BleakClient(mac_address, timeout = 10) as client:
        
            dateTimeObj = datetime.now()
            date = bytes([dateTimeObj.second, dateTimeObj.minute, dateTimeObj.hour, dateTimeObj.day, dateTimeObj.year % 100])

            await client.write_gatt_char("4d4f4445-5343-4f2d-574f-524a45523033", data = date)

            # User code is in ASCII numbers
            # TODO: Replace with correct user code in ASCII numbers
            # See: https://www.asciitable.com/
            code = bytes([49, 51, 48, 57, 48, 48, 49])
            
            # Write data to characteristic
            await client.write_gatt_char("4d4f4445-5343-4f2d-574f-524a45523032", data = code)

            return True

    except Exception as ex:
        logger.debug(ex)
        return False

async def get_lock_status(mac_address):

    global status_retrieved
    status_retrieved = False
    
    status = {}

    def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
        if(device.name == "PSLOCK" and device.address == mac_address):
            logger.debug(f"{device.address}")
            logger.debug(advertisement_data.manufacturer_data)

            adv_bytes = advertisement_data.manufacturer_data.get(65535)
            logger.debug(list(adv_bytes))
            logger.debug(f"Battery level: {list(adv_bytes)[0]} %")
            logger.debug(f"Lock state: {list(adv_bytes)[3]}")
            logger.debug(f"Door state: {list(adv_bytes)[4]}")
            logger.debug(f"Open time: {list(adv_bytes)[6]}")

            status["battery_level"] = list(adv_bytes)[0]
            status["lock_state"] = list(adv_bytes)[3]
            status["door_state"] = list(adv_bytes)[4]
            status["open_time"] = list(adv_bytes)[6]

            global status_retrieved
            status_retrieved = True

    scanner = BleakScanner(detection_callback, ["4d4f4445-5343-4f2d-574f-514b45523232"])
    
    while not status_retrieved:
        logger.debug("(re)starting scanner")
        await scanner.start()
        await asyncio.sleep(5.0)
        await scanner.stop()
        
    return status

async def unlock(mac_address, num_retries = 5):
    
    retries = 0
    success = False
    while(not success or retries >= num_retries):
        retries = retries + 1 
        logger.debug(f"Attempt {retries} to open the lock.")
        success = await _unlock(mac_address)
    
    if(not success):
        logger.error(f"Unable to open lock within {num_retries} attempts.")

    return success
    
# Main entry into the user prompt
async def main():

    prompt = ""
    while(prompt != "exit"):
        prompt = input("Please type a command (unlock, status, exit): ")

        if(prompt == "unlock"):

            mac_address = input("Enter mac-address (default: DE:44:38:02:AA:EA): ")
            if mac_address == "":
                mac_address = "DE:44:38:02:AA:EA"

            print(f"Unlocking {mac_address}")
            result = await unlock(mac_address)
            print(f"Unlock successful? { result }")

        elif(prompt == "status"):

            mac_address = input("Enter mac-address (default: DE:44:38:02:AA:EA): ")
            if mac_address == "":
                mac_address = "DE:44:38:02:AA:EA"
            
            print(f"Retrieving status for {mac_address}")
            status = await get_lock_status(mac_address)
            print(f"Status: {status}")

        elif(prompt == "exit"):
            print("Bye bye!")


asyncio.run(main())