from importlib.metadata import requires
import requests
import json
import time

carbideEndPoint = "http://127.0.0.1:20010"  # SDK emulated laser
# carbideEndPoint = "http://192.168.240.10:20018" # for real laser
# pharosEndPoint = "http://127.0.0.1:20010"  # SDK emulated laser
# pharosEndPoint = "http://192.168.240.10:20018" # for real laser


class carbide:
    """Control over Carbide laser
    """
    def __init__(self):
        self.laserIdentificationNumber()
        self.serialNumber()
        self.requestHeaders = {"Content-Type": "application/json"}

    def laserIdentificationNumber(self):
        """_summary_
        """
        self.laseridentificationnumber = requests.get(
            f"{carbideEndPoint}/v1/Basic/LaserIdentificationNumber")
        if self.laseridentificationnumber.status_code == 200:
            print(f"Laser ID: {self.laseridentificationnumber.text}")
        else:
            print("Not sure about ID")

    def serialNumber(self):
        """_summary_
        """
        self.serialnumber = requests.get(
            f"{carbideEndPoint}/v1/Basic/SerialNumber")
        if self.serialnumber.status_code == 200:
            print(f"Laser Serial Number: {self.serialnumber.text}")
        else:
            print("Not sure about serial number")

    def isOutputEnabled(self):
        """_summary_
        """
        self.isoutputenabled = requests.get(
            f"{carbideEndPoint}/v1/Basic/IsOutputEnabled")
        if self.isoutputenabled.status_code == 200:
            if self.isoutputenabled.text == "true":
                print("Output is open")
            elif self.isoutputenabled.text == "false":
                print("Output is closed")
            else:
                pass
        else:
            print("Not sure about output status")

    def selectAndApplyPreset(self, preset="1"):
        """Select preset, default of 1, apply the preset and wait for the laser to become operational

        Args:
            preset (str, optional): Preset to use as set in GUI. Defaults to "1".
        """
        self.currentpreset = requests.get(
            f"{carbideEndPoint}/v1/Basic/SelectedPresetIndex")
        if self.currentpreset.status_code == 200:
            print(f"Current preset is {self.currentpreset.text}")
        else:
            print("No idea what current preset is")
        print(f"Requesting preset {preset}")
        presetNumber = int(preset)
        self.selectpreset = requests.put(
            f"{carbideEndPoint}/v1/Basic/SelectedPresetIndex", data=json.dumps(presetNumber), headers=self.requestHeaders)
        if self.selectpreset.status_code == 200:
            print(f"Preset {preset} has been set, applying...")
            self.applypreset = requests.post(
                f"{carbideEndPoint}/v1/Basic/ApplySelectedPreset", headers=self.requestHeaders)
            time.sleep(2)
            if self.applypreset.status_code == 200:
                self.waitForLaserOperational()
                print("Successfully applied!")
            elif self.applypreset.status_code == 403:
                print("Could not apply preset")
            else:
                print("Error applying preset")
        elif self.selectpreset.status_code == 403:
            print("Preset doesn't exist. Check available presets")
        else:
            print("Error setting preset")

    def changeOutput(self, state="close"):
        """_summary_

        Args:
            state (str, optional): _description_. Defaults to "close".
        """
        print(f"Requesting output {state}")
        if state == "enable":
            self.enableoutput = requests.post(
                f"{carbideEndPoint}/v1/Basic/EnableOutput", headers=self.requestHeaders)
            if self.enableoutput.status_code == 200:
                print("Output enabled")
            elif self.enableoutput.status_code == 403:
                print("Cannot enable output, check state")
            else:
                print("Set output enable error")
        elif state == "close":
            self.closeoutput = requests.post(
                f"{carbideEndPoint}/v1/Basic/CloseOutput", headers=self.requestHeaders)
            if self.closeoutput.status_code == 200:
                print("Output closed")
            elif self.closeoutput.status_code == 403:
                print("Laser not running anyway")
            else:
                print("Set output close error")

    def waitForLaserOperational(self):
        """Wait for laser to reach operational state, break if in failure state
        """        
        self.actualStateName()
        while self.actualstatename.text != "\"Operational\"":
            print(self.actualstatename.text)
            time.sleep(1)
            self.actualStateName()
            if self.actualstatename.text == "\"Failure\"":
                print("Laser in failure state. Stopping...")
                break
            else:
                pass
        if self.actualstatename.text == "\"Operational\"":
            print("Laser in operational state, ready to enable output")

    def actualStateName(self):
        """Get current state of laser
        """
        self.actualstatename = requests.get(
            f"{carbideEndPoint}/v1/Basic/ActualStateName")

    def goToStandby(self):
        self.gotostandby = requests.post(f"{carbideEndPoint}/v1/Basic/GoToStandby", headers=self.requestHeaders)
        if self.gotostandby.status_code == 200:
            self.actualStateName()
            while self.actualstatename != "\"StandingBy\"":
                time.sleep(1)
                self.actualStateName()
            if self.actualstatename == "\"StandingBy\"":
                print("Laser in standby")
            else:
                print("Laser not in standby, please check state manually")

if __name__ == "__main__":
    run = carbide()
    run.isOutputEnabled()
    run.selectAndApplyPreset("2")
    run.changeOutput("enable")
    time.sleep(5)
    run.changeOutput()
