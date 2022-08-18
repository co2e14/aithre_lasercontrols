# This example scenario shows how to use Carbide laser via API.
import requests
import json
import time

# Let's use default laser IP address.
laserEndPoint = "http://127.0.0.1:20010"

# Reading current preset index.
response = requests.get(laserEndPoint + "/v1/Basic/SelectedPresetIndex")
if response.status_code == 200:
    # Operation succeeded.
    print("Current selected preset index is: " + response.text)
else:
    print("Can't get selected preset index.")


# Changing selected preset index to 1.
# Each request is serialized in JSON format.
requestHeaders = {"Content-Type": "application/json"}
response = requests.put(
    laserEndPoint + "/v1/Basic/SelectedPresetIndex",
    data=json.dumps(1),
    headers=requestHeaders,
)
if response.status_code == 200:
    # Operation succeeded.
    print("Selected preset with index - 1.")
else:
    print("Can't set selected preset index.")


# Apply selected preset. This will trigger preset execution.
response = requests.post(
    laserEndPoint + "/v1/Basic/ApplySelectedPreset", headers=requestHeaders
)
if response.status_code == 200:
    # Operation succeeded.
    print("Successfully triggered preset execution.")
else:
    print("Failed to trigger preset execution.")


# Wait while laser goes to "Operational" state.
response = requests.get(laserEndPoint + "/v1/Basic/ActualStateName")
if response.status_code == 200:
    while response.text != '"Operational"':
        time.sleep(1)
        response = requests.get(laserEndPoint + "/v1/Basic/ActualStateName")

    print("Laser state is operational. We can start working.")
else:
    print("Failed to get actual state.")


# Enable output.
response = requests.post(
    laserEndPoint + "/v1/Basic/EnableOutput", headers=requestHeaders
)
print("Output is enabled. Laser is working.")

# Wait for 1 sec.
time.sleep(1)

# Close output.
response = requests.post(
    laserEndPoint + "/v1/Basic/CloseOutput", headers=requestHeaders
)
print("Output is closed. Laser is not working.")

# When job is done leave laser at standing by state.
response = requests.post(
    laserEndPoint + "/v1/Basic/GoToStandby", headers=requestHeaders
)
print("Laser is going to standby state. We can safely leave for good.")
