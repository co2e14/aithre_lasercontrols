from importlib.metadata import requires
import requests
import json
import time

# carbideEndPoint = "http://127.0.0.1:20010"  # SDK emulated laser
# carbideEndPoint = "http://192.168.240.10:20018" # for real laser
# pharosEndPoint = "http://127.0.0.1:20010"  # SDK emulated laser
# pharosEndPoint = "http://192.168.240.10:20018" # for real laser


class carbide:
    """Control over Carbide laser
    """

    def __init__(self):
        self.carbideEndPoint = "http://127.0.0.1:20010"
        self.laserIdentificationNumber()
        self.serialNumber()
        self.currentaomtriggersource = 0
        self.requestHeaders = {"Content-Type": "application/json"}

    def laserIdentificationNumber(self):
        """_summary_
        """
        self.laseridentificationnumber = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/LaserIdentificationNumber"
        )
        if self.laseridentificationnumber.status_code == 200:
            print(f"Laser ID: {self.laseridentificationnumber.text}")
        else:
            print("Not sure about ID")

    def serialNumber(self):
        """_summary_
        """
        self.serialnumber = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/SerialNumber"
        )
        if self.serialnumber.status_code == 200:
            print(f"Laser Serial Number: {self.serialnumber.text}")
        else:
            print("Not sure about serial number")

    def isOutputEnabled(self):
        """_summary_
        """
        self.isoutputenabled = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/IsOutputEnabled"
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
        """Select preset, apply preset, and wait for the laser to become operational

        Args:
            preset (str, optional): Preset to use as set in GUI. Defaults to "1".
        """
        self.currentpreset = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/SelectedPresetIndex"
        )
        if self.currentpreset.status_code == 200:
            print(f"Current preset is {self.currentpreset.text}")
        else:
            print("No idea what current preset is")
        print(f"Requesting preset {preset}")
        presetNumber = int(preset)
        self.selectpreset = requests.put(
            f"{self.carbideEndPoint}/v1/Basic/SelectedPresetIndex",
            data=json.dumps(presetNumber),
            headers=self.requestHeaders,
        )
        if self.selectpreset.status_code == 200:
            print(f"Preset {preset} has been set, applying...")
            self.applypreset = requests.post(
                f"{self.carbideEndPoint}/v1/Basic/ApplySelectedPreset",
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
                f"{self.carbideEndPoint}/v1/Basic/EnableOutput",
                headers=self.requestHeaders,
            )
            if self.enableoutput.status_code == 200:
                print("Output enabled")
            elif self.enableoutput.status_code == 403:
                print("Cannot enable output, check state")
            else:
                print("Set output enable error")
        elif state == "close":
            self.closeoutput = requests.post(
                f"{self.carbideEndPoint}/v1/Basic/CloseOutput",
                headers=self.requestHeaders,
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
            f"{self.carbideEndPoint}/v1/Basic/ActualStateName"
        )

    def goToStandby(self):
        """_summary_
        """
        self.gotostandby = requests.post(
            f"{self.carbideEndPoint}/v1/Basic/GoToStandby", headers=self.requestHeaders
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

    def actualValues(self):
        """_summary_
        """
        self.actualattenuatorpercentage = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/ActualAttenuatorPercentage"
        )
        if self.actualattenuatorpercentage.status_code == 200:
            self.actualattenuatorpercentage_float = float(
                self.actualattenuatorpercentage.text
            )
            print(f"Attenuator percentage: {self.actualattenuatorpercentage.text}%")
        else:
            pass
        self.actualoutputenergy = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/ActualOutputEnergy"
        )
        if self.actualoutputenergy.status_code == 200:
            print(f"Output energy: {self.actualoutputenergy.text} uJ")
        else:
            pass
        self.actualoutputfrequency = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/ActualOutputFrequency"
        )
        if self.actualoutputfrequency.status_code == 200:
            print(f"Output frequency: {self.actualoutputfrequency.text} kHz")
        else:
            pass
        self.actualoutputpower = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/ActualOutputPower"
        )
        if self.actualoutputpower.status_code == 200:
            print(f"Output power: {self.actualoutputpower.text} W")
        else:
            pass
        self.actualpulseduration = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/ActualPulseDuration"
        )
        if self.actualpulseduration.status_code == 200:
            print(f"Pulse duration: {self.actualpulseduration.text} fs")
        else:
            pass
        self.actualPpdivider = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/ActualPpDivider"
        )
        if self.actualPpdivider.status_code == 200:
            print(f"Pulse picker divider: {self.actualPpdivider.text}")
        else:
            pass
        self.actualshutterstate = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/ActualShutterState"
        )
        if self.actualshutterstate.status_code == 200:
            print(f"Shutter state: {self.actualshutterstate.text}")
        else:
            pass
        self.actualrafrequency = requests.get(
            f"{self.carbideEndPoint}/v1/Advanced/ActualRaFrequency"
        )
        if self.actualrafrequency.status_code == 200:
            print(f"RA frequency: {self.actualrafrequency.text} Hz")
        else:
            pass
        self.actualstateid = requests.get(
            f"{self.carbideEndPoint}/v1/Advanced/ActualStateId"
        )
        if self.actualstateid.status_code == 200:
            print(f"State ID no.: {self.actualstateid.text}")
        else:
            pass
        self.actualharmonic = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/ActualHarmonic"
        )
        if self.actualharmonic.status_code == 200:
            self.wavelength = int(1030 / int(self.actualharmonic.text))
            print(
                f"Using harmonic {self.actualharmonic.text}, {str(self.wavelength)}nm"
            )
        else:
            print("Unable to find harmonic")

    def targetAttenuatorPercentage(self, percentage="0"):
        """_summary_

        Args:
            percentage (str, optional): percentage to request. Defaults to "0".
        """
        self.settargetattenuatorpercentage = requests.put(
            f"{self.carbideEndPoint}/v1/Basic/TargetAttenuatorPercentage",
            data=json.dumps(percentage),
            headers=self.requestHeaders,
        )
        if self.settargetattenuatorpercentage.status_code == 200:
            self.gettargetattenuatorpercentage = requests.get(
                f"{self.carbideEndPoint}/v1/Basic/TargetAttenuatorPercentage"
            )
            if self.gettargetattenuatorpercentage.status_code == 200:
                while int(self.gettargetattenuatorpercentage.text) != int(
                    self.actualattenuatorpercentage.text
                ):
                    print(
                        f"Target attenuator percentage is {self.gettargetattenuatorpercentage.text}, currently at {self.actualattenuatorpercentage.text}"
                    )
            else:
                print("Cannot get requested attenuator percentage")
        elif self.settargetattenuatorpercentage.status_code == 403:
            print(f"Cannot set to this value, likely out of bounds")
        else:
            print("Error setting target attenuator percentage")

    def targetPulseDuration(self, length="290"):
        """_summary_

        Args:
            length (str, optional): pulse length to request (-ve = negative chirp, otherwise positive). 
            Defaults to "290".
        """
        self.settargetpulseduration = requests.put(
            f"{self.carbideEndPoint}/v1/Basic/TargetPulseDuration",
            data=json.dumps(length),
            headers=self.requestHeaders,
        )
        if self.settargetpulseduration.status_code == 200:
            self.gettargetpulseduration = requests.get(
                f"{self.carbideEndPoint}/v1/Basic/TargetPulseDuration"
            )
            if self.gettargetpulseduration.status_code == 200:
                while int(self.gettargetpulseduration.text) != int(
                    self.actualpulseduration.text
                ):
                    print(
                        f"Target pulse duration is {self.gettargetpulseduration.text}, currently at {self.actualpulseduration.text}"
                    )
            else:
                print("Cannot get requested pulse duration")
        elif self.settargetpulseduration.status_code == 403:
            print(f"Cannot set to this value, likely out of bounds")
        else:
            print("Error setting pulse duration")

    def targetPpDivider(self, divider="1000"):
        """_summary_

        Args:
            divider (str, optional): _description_. Defaults to "1000".
        """
        self.settargetppdivider = requests.put(
            f"{self.carbideEndPoint}/v1/Basic/TargetPpDivider",
            data=json.dumps(divider),
            headers=self.requestHeaders,
        )
        if self.settargetppdivider.status_code == 200:
            self.gettargetppdivider = requests.get(
                f"{self.carbideEndPoint}/v1/Basic/TargetPpDivider"
            )
            if self.gettargetppdivider.status_code == 200:
                while int(self.gettargetppdivider.text) != int(
                    self.actualPpdivider.text
                ):
                    print(
                        f"Target pulse picker divider is {self.gettargetppdivider.text}, currently at {self.actualPpdivider.text}"
                    )
            else:
                print("Cannot get requested pulse duration")
        elif self.settargetppdivider.status_code == 403:
            print(f"Cannot set to this value, likely out of bounds")
        else:
            print("Error setting divider")

    def isRemoteInterlockActive(self):
        """_summary_
        """
        self.isremoteinterlockactive = requests.get(
            f"{self.carbideEndPoint}/v1/Advanced/IsRemoteInterlockActive"
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
        """_summary_
        """
        self.resetremoteinterlock = requests.post(
            f"{self.carbideEndPoint}/v1/Advanced/ResetRemoteInterlock",
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
        """_summary_
        """
        self.isppenabled = requests.get(
            f"{self.carbideEndPoint}/v1/Advanced/IsPpEnabled"
        )
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
        """Enable or disable the carbide pulse picker

        Args:
            toggle (str, optional): option to toggle the pulse picker on or off. 
            Defaults to "off".
        """
        if toggle == "off":
            self.enablepp = requests.post(
                f"{self.carbideEndPoint}/v1/Advanced/EnablePp",
                headers=self.requestHeaders,
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
                f"{self.carbideEndPoint}/v1/Advanced/DisablePp",
                headers=self.requestHeaders,
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

    def getAomTriggerSource(self):
        """_summary_
        """
        self.getaomtriggersource = requests.get(
            f"{self.carbideEndPoint}/v1/ExternalControl/AomTriggerSource"
        )
        if self.getaomtriggersource.status_code == 200:
            print(f"AOM trigger source is set to {self.getaomtriggersource.text}")
            if self.getaomtriggersource.text == '"Internal"':
                self.currentaomtriggersource = 1
            elif self.getaomtriggersource.text == '"ExternalLow"':
                self.currentaomtriggersource = 2
            elif self.getaomtriggersource.text == '"ExternalHigh"':
                self.currentaomtriggersource = 3
            else:
                print("Unknown current trigger source")
                self.currentaomtriggersource = 0
        else:
            print("Cannot get AOM trigger source")

    def setAomTriggerSource(self, source="Internal"):
        """_summary_

        Args:
            source (str, optional): Trigger control source, can be Internal, ExternalHigh or ExternalLow. 
            Defaults to "Internal".
        """
        self.setaomtriggersource = requests.put(
            f"{self.carbideEndPoint}/v1/ExternalControl/AomTriggerSource",
            data=json.dumps(source),
            headers=self.requestHeaders,
        )
        if self.setaomtriggersource.status_code == 200:
            self.getAomTriggerSource()
        elif self.setaomtriggersource.status_code == 403:
            print("Could not set trigger source")
            self.getAomTriggerSource()
        else:
            print("Error setting trigger source")

    def isPowerlockEnabled(self):
        """_summary_
        """
        self.ispowerlockenabled = requests.get(
            f"{self.carbideEndPoint}/v1/Basic/IsPowerlockEnabled"
        )
        if self.ispowerlockenabled.status_code == 200:
            if self.ispowerlockenabled.text == "true":
                self.powerlockstatus = "enabled"
            elif self.ispowerlockenabled.text == "false":
                self.powerlockstatus = "disabled"
            else:
                pass
            print(f"Powerlock is currently {self.powerlockstatus}")
        else:
            pass

    def powerlockControl(self, state="enable"):
        """_summary_

        Args:
            state (str, optional): _description_. Defaults to "enable".
        """
        if state == "enable":
            self.enablepowerlock = requests.post(
                f"{self.carbideEndPoint}/v1/Basic/EnablePowerlock",
                headers=self.requestHeaders,
            )
            if self.enablepowerlock.status_code == 200:
                print("Enabling powerlock...")
                while self.powerlockstatus != "enabled":
                    time.sleep(1)
                    self.isPowerlockEnabled()
            elif self.enablepowerlock.status_code == 403:
                print("Unable to enable powerlock")
            else:
                print("Error enabling powerlock")
        elif state == "disable":
            self.disablepowerlock = requests.post(
                f"{self.carbideEndPoint}/v1/Basic/DisablePowerlock",
                headers=self.requestHeaders,
            )
            if self.disablepowerlock.status_code == 200:
                print("Disabling powerlock...")
                while self.powerlockstatus != "disabled":
                    time.sleep(1)
                    self.isPowerlockEnabled()
            elif self.disablepowerlock.status_code == 403:
                print("Unable to disable powerlock")
            else:
                print("Error disabling powerlock")

    def reduceLeak(self):
        """Algo to recduce PP leakage. Use after at least 2 hours of laser running.
        """
        self.reduceleak = requests.post(
            f"{self.carbideEndPoint}/v1/Advanced/ReduceLeak"
        )
        if self.reduceleak.status_code == 200:
            print("Reducing leak...")
            time.sleep(3)
            print("Leak reduction successfull")
        elif self.reduceleak.status_code == 403:
            print("Unable to run leak reduction")


if __name__ == "__main__":
    run = carbide()
    run.isOutputEnabled()
    run.actualValues()
    run.selectAndApplyPreset("1")

