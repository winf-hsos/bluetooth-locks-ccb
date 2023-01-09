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

scan_task = None
devices = {}
devices_status = {}

def _device_detected(device: BLEDevice, advertisement_data: AdvertisementData):

    logger.debug(f"Device detected: {device}")

    global devices
    if(device.name == "PSLOCK"):
        logger.debug(f"Found PSLOCK: { device.address}")

        if not device.address in devices:
            logger.debug(f"Device { device.address} is not in list yet. Adding it.")    
        else:
            logger.debug(f"Device { device.address} is already in list. Refreshing it.")    

        devices[device.address] = device


        adv_bytes = advertisement_data.manufacturer_data.get(65535)
        status = {}
        status["timestamp"] = datetime.now()
        status["battery_level"] = list(adv_bytes)[0]
        status["lock_state"] = list(adv_bytes)[3]
        status["door_state"] = list(adv_bytes)[4]
        status["open_time"] = list(adv_bytes)[6]

        devices_status[device.address] = status
    else:
        logger.debug(f"Found a device that is not a PSLOCK: { device.name }")

async def _start_continuous_scan():
    scanner = BleakScanner(_device_detected, service_uuids=["4d4f4445-5343-4f2d-574f-514b45523232"])

    while True:
        logger.debug("(re)starting scanner")
        await scanner.start()
        await asyncio.sleep(10.0)
        await scanner.stop()
    
async def _unlock(mac_address, user_code = "1234"):
    try:
        global devices
        if(mac_address in devices):
            client = BleakClient(devices.get(mac_address))
        else:
            client = BleakClient(mac_address, timeout = 10)

        async with client:
        
            dateTimeObj = datetime.now()
            date = bytes([dateTimeObj.second, dateTimeObj.minute, dateTimeObj.hour, dateTimeObj.day, dateTimeObj.year % 100])

            await client.write_gatt_char("4d4f4445-5343-4f2d-574f-524a45523033", data = date)

            # User code is in ASCII numbers
            # TODO: Replace with correct user code in ASCII numbers
            # See: https://www.asciitable.com/
            code = bytes([ord(user_code[0]), ord(user_code[1]), ord(user_code[2]), ord(user_code[3]), 48, 48, 49])
            
            # Write data to characteristic
            await client.write_gatt_char("4d4f4445-5343-4f2d-574f-524a45523032", data = code)

            return True

    except Exception as ex:
        logger.debug(ex)
        return False

def get_lock_status(mac_address):
    status = devices_status.get(mac_address)
    
    if status == None:
        logger.error(f"Device { mac_address } not found (yet).")
    
    return status

async def unlock(mac_address, user_code = "1234", num_retries = 1):
    
    retries = 0
    success = False
    while(not success or retries < num_retries):
        retries = retries + 1 
        logger.debug(f"Attempt {retries} to open the lock.")
        success = await _unlock(mac_address, user_code)
    
    if(not success):
        logger.error(f"Unable to open lock { mac_address } within {num_retries} attempts.")

    return success

async def start(device_name = "PSLOCK"):
    scan = _start_continuous_scan()

    global scan_task
    scan_task = asyncio.create_task(scan)
    await asyncio.sleep(0)

def stop():
    global scan_task
    scan_task.cancel() 