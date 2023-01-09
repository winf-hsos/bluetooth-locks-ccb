import asyncio
from pslock_api import start, stop, unlock, get_lock_status

# Main entry into the user prompt
async def main():

    await start()
    
    prompt = ""
    while(prompt != "exit"):
        await asyncio.sleep(0)
        prompt = input("Please type a command (unlock, status, exit): ")
        await asyncio.sleep(0)

        if(prompt == "unlock"):

            mac_address = input("Enter mac-address (default: DE:44:38:02:AA:EA): ")
            if mac_address == "":
                mac_address = "DE:44:38:02:AA:EA"
            
            user_code = input("Enter user code (default: 1234): ")
            
            print(f"Unlocking {mac_address}")
            result = await unlock(mac_address, user_code)
            print(f"Unlock successful? { result }")

        elif(prompt == "status"):

            mac_address = input("Enter mac-address (default: DE:44:38:02:AA:EA): ")
            if mac_address == "":
                mac_address = "DE:44:38:02:AA:EA"
            
            print(f"Retrieving status for {mac_address}")
            status = get_lock_status(mac_address)
            print(f"Status: {status}")

        elif(prompt == "exit"):
            stop()
            print("Bye bye!")


asyncio.run(main())