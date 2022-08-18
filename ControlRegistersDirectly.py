# This example scenario shows how to get / set concrete registers data.
import requests
import json

# Let's use default laser IP address.
laserEndPoint = "http://127.0.0.1:20060"

# Reading ActualOutputPower register.
response = requests.get(laserEndPoint + "/v1/register/0x53026000")
if response.status_code == 200:
    # Operation succeeded.
    print("Actual power is: " + response.text)
else:
    print("Can't get actual power value.")

shutterState = -1
# Checking shutter state.
response = requests.get(laserEndPoint + "/v1/register/0x53007100")
if response.status_code == 200:
    # Operation succeeded.
    shutterState = int(response.text)
    print("Shutter state is: " + response.text)
else:
    shutterState = 0
    print("Can't get Shutter state value.")

# Close output if it is enabled.
if shutterState == 2:
    # Close output.
    # Set register accepts only value 0x00AA00AA (see documentation).
    response = requests.put(
        laserEndPoint + "/v1/register/0x5300A000",
        data=json.dumps(0x00AA00AA),
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 200:
        print("Output successfully closed.")
    else:
        print("Failed to close output.")
