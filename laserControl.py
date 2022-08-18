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
            f"{carbideEndPoint}/v1/Basic/LaserIdentificationNumber"
        )
        if self.laseridentificationnumber.status_code == 200:
            print(f"Laser ID: {self.laseridentificationnumber.text}")
        else:
            print("Not sure about ID")

    def serialNumber(self):
        """_summary_
        """
        self.serialnumber = requests.get(f"{carbideEndPoint}/v1/Basic/SerialNumber")
        if self.serialnumber.status_code == 200:
            print(f"Laser Serial Number: {self.serialnumber.text}")
        else:
            print("Not sure about serial number")

    def isOutputEnabled(self):
        """_summary_
        """
        self.isoutputenabled = requests.get(
            f"{carbideEndPoint}/v1/Basic/IsOutputEnabled"
        )
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
            f"{carbideEndPoint}/v1/Basic/SelectedPresetIndex"
        )
        if self.currentpreset.status_code == 200:
            print(f"Current preset is {self.currentpreset.text}")
        else:
            print("No idea what current preset is")
        print(f"Requesting preset {preset}")
        presetNumber = int(preset)
        self.selectpreset = requests.put(
            f"{carbideEndPoint}/v1/Basic/SelectedPresetIndex",
            data=json.dumps(presetNumber),
            headers=self.requestHeaders,
        )
        if self.selectpreset.status_code == 200:
            print(f"Preset {preset} has been set, applying...")
            self.applypreset = requests.post(
                f"{carbideEndPoint}/v1/Basic/ApplySelectedPreset",
                headers=self.requestHeaders,
            )
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
                f"{carbideEndPoint}/v1/Basic/EnableOutput", headers=self.requestHeaders
            )
            if self.enableoutput.status_code == 200:
                print("Output enabled")
            elif self.enableoutput.status_code == 403:
                print("Cannot enable output, check state")
            else:
                print("Set output enable error")
        elif state == "close":
            self.closeoutput = requests.post(
                f"{carbideEndPoint}/v1/Basic/CloseOutput", headers=self.requestHeaders
            )
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
        while self.actualstatename.text != '"Operational"':
            print(self.actualstatename.text)
            time.sleep(1)
            self.actualStateName()
            if self.actualstatename.text == '"Failure"':
                print("Laser in failure state. Stopping...")
                break
            else:
                pass
        if self.actualstatename.text == '"Operational"':
            print("Laser in operational state, ready to enable output")

    def actualStateName(self):
        """Get current state of laser
        """
        self.actualstatename = requests.get(
            f"{carbideEndPoint}/v1/Basic/ActualStateName"
        )

    def goToStandby(self):
        self.gotostandby = requests.post(
            f"{carbideEndPoint}/v1/Basic/GoToStandby", headers=self.requestHeaders
        )
        if self.gotostandby.status_code == 200:
            self.actualStateName()
            while self.actualstatename != '"StandingBy"':
                time.sleep(1)
                self.actualStateName()
            if self.actualstatename == '"StandingBy"':
                print("Laser in standby")
            else:
                print("Laser not in standby, please check state manually")

    def actualHarmonic(self):
        self.actualharmonic = requests.get(f"{carbideEndPoint}/v1/Basic/ActualHarmonic")
        if self.actualharmonic.status_code == 200:
            self.wavelength = int(1030 / int(self.actualharmonic.text))
            print(
                f"Using harmonic {self.actualharmonic.text}, {str(self.wavelength)}nm"
            )
        else:
            print("Unable to find harmonic")

    def actualValues(self):
        self.actualattenuatorpercentage = requests.get(
            f"{carbideEndPoint}/v1/Basic/ActualAttenuatorPercentage"
        )
        if self.actualattenuatorpercentage.status_code == 200:
            self.actualattenuatorpercentage_float = float(
                self.actualattenuatorpercentage.text
            )
            print(f"Power percentage: {self.actualattenuatorpercentage.text}%")
        else:
            pass
        self.actualoutputenergy = requests.get(
            f"{carbideEndPoint}/v1/Basic/ActualOutputEnergy"
        )
        if self.actualoutputenergy.status_code == 200:
            print(f"Output energy: {self.actualoutputenergy.text} uJ")
        else:
            pass
        self.actualoutputfrequency = requests.get(
            f"{carbideEndPoint}/v1/Basic/ActualOutputFrequency"
        )
        if self.actualoutputfrequency.status_code == 200:
            print(f"Output frequency: {self.actualoutputfrequency.text} kHz")
        else:
            pass
        self.actualoutputpower = requests.get(
            f"{carbideEndPoint}/v1/Basic/ActualOutputPower"
        )
        if self.actualoutputpower.status_code == 200:
            print(f"Output power: {self.actualoutputpower.text} W")
        else:
            pass
        self.actualpulseduration = requests.get(
            f"{carbideEndPoint}/v1/Basic/ActualPulseDuration"
        )
        if self.actualpulseduration.status_code == 200:
            print(f"Pulse duration: {self.actualpulseduration.text} fs")
        else:
            pass
        self.actualPpdivider = requests.get(
            f"{carbideEndPoint}/v1/Basic/ActualPpDivider"
        )
        if self.actualPpdivider.status_code == 200:
            print(f"Pulse picker divider: {self.actualPpdivider.text}")
        else:
            pass

    def isRemoteInterlockActive(self):
        self.isremoteinterlockactive = requests.get(
            f"{carbideEndPoint}/v1/Advanced/IsRemoteInterlockActive"
        )
        if self.isremoteinterlockactive.status_code == 200:
            if self.isremoteinterlockactive.text == "true":
                print("Remote interlock armed")
            elif self.isremoteinterlockactive.text == "false":
                print("Remote interlock is NOT armed")
            else:
                pass
        else:
            print("Cannot get remote interlock state")

    def resetRemoteInterlock(self):
        self.resetremoteinterlock = requests.post(
            f"{carbideEndPoint}/v1/Advanced/ResetRemoteInterlock",
            headers=self.requestHeaders,
        )
        if self.resetremoteinterlock.status_code == 200:
            print("Remote interlock reset")
            self.isRemoteInterlockActive()
        elif self.resetremoteinterlock.status_code == 403:
            print("Cannot reset remote interlock")
            self.isRemoteInterlockActive()
        else:
            print("Error resetting remote interlock")

    def isPpEnabled(self):
        self.isppenabled = requests.get(f"{carbideEndPoint}/v1/Advanced/IsPpEnabled")
        if self.isppenabled.status_code == 200:
            if self.isppenabled.text == "true":
                print("Pule picker is enabled")
                self.pulsepickerstatus = True
            elif self.isppenabled.text == "false":
                print("Pulse picker not enabled")
                self.pulsepickerstatus = False
            else:
                print("Can't get pulse picker status")
        else:
            print("Error getting pulse picker status")

    def togglePulsePicker(self, toggle="off"):
        if toggle == "off":
            self.enablepp = requests.post(
                f"{carbideEndPoint}/v1/Advanced/EnablePp", headers=self.requestHeaders
            )
            if self.enablepp.status_code == 200:
                print("Enabling pulse picker")
                self.isPpEnabled()
            elif self.enablepp.status_code == 403:
                print("Could not enable pulse picker")
                self.isPpEnabled()
            else:
                print("Error enabling pulse picker")
                self.isPpEnabled()
        elif toggle == "on":
            self.disablepp = requests.post(
                f"{carbideEndPoint}/v1/Advanced/DisablePp", headers=self.requestHeaders
            )
            if self.disablepp.status_code == 200:
                print("Disabling pulse picker")
                self.isPpEnabled()
            elif self.disablepp.status_code == 403:
                print("Could not disable pulse picker (probably already disabled")
                self.isPpEnabled()
            else:
                print("Error disabling pulse picker")
                self.isPpEnabled()
        else:
            print(f"Unknown request of pulse picker state: {toggle}")


if __name__ == "__main__":
    run = carbide()
    run.isOutputEnabled()
    run.actualValues()
    run.selectAndApplyPreset("2")
    run.changeOutput("enable")
    time.sleep(5)
    run.changeOutput()
    run.actualHarmonic()
