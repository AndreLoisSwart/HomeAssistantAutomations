from appdaemon.plugins.hass import hassapi as hass
from firmware_logic import check_firmware_mismatch


class FirmwareCheck(hass.Hass):
    def initialize(self):
        print("FIRMWARE_CHECK: initialize() called")
        self.debug = self.args.get("debug", False)
        self.notify_target = self.args.get("notify_target")
        interval = self.args.get("check_interval_seconds", 3600)
        self.run_every(self.scheduled_check, "immediate", interval)

    async def scheduled_check(self, kwargs):
        self.log("Starting firmware check", level="INFO")
        try:
            result = await check_firmware_mismatch(
                self.args["router_host"],
                self.args["router_username"],
                self.args["router_password"],
            )
        except Exception as e:
            self.log(f"Firmware check failed: {e}", level="ERROR")
            self.set_state(
                "sensor.aimesh_firmware_status",
                state="error",
                attributes={"error": str(e)},
            )
            return
        self.log("Firmware check completed", level="INFO")

        devices = {
            mac: {"type": info.device_type, "fw": info.fw}
            for mac, info in result.device_info.items()
        }
        self.set_state(
            "sensor.aimesh_firmware_status",
            state="mismatch" if result.mismatch else "ok",
            attributes={
                "devices": devices,
                "friendly_name": "AiMesh Firmware Status",
                "error": None,
            },
        )

        if result.mismatch:
            lines = [
                f"{info['type']}: {mac} → {info['fw']}" for mac, info in devices.items()
            ]
            message = "Firmware mismatch:\n" + "\n".join(lines)

            if self.debug:
                self.log(message, level="INFO")
            elif self.notify_target:
                self.notify(
                    message, title="AiMesh firmware mismatch", name=self.notify_target
                )
