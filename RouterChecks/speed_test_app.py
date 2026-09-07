from appdaemon.plugins.hass import hassapi as hass
from speed_test_logic import (
    build_speedtest_config,
    get_speed_test_data,
    parse_speedtest_result,
    trigger_speed_test,
)

CONNECTION_SPEED = 240.00
ISSUE_THRESHOLD = 0.6


class SpeedtestCheck(hass.Hass):
    def initialize(self):
        self.debug = self.args.get("debug", False)
        self.notify_target = self.args.get("notify_target")
        self.check_in_progress = False
        interval = self.args.get("check_interval_seconds", 7200)
        self.run_every(self.scheduled_check, "immediate", interval)

    async def scheduled_check(self, kwargs):
        if self.check_in_progress:
            self.log(
                "Previous speedtest still running, skipping this cycle", level="WARNING"
            )
            return

        self.check_in_progress = True
        self.log("Triggering speedtest", level="INFO")

        try:
            config = build_speedtest_config(
                self.args["router_host"],
                self.args["router_username"],
                self.args["router_password"],
            )

            await trigger_speed_test(config)
        except Exception as e:
            self.log(f"Speedtest check failed: {e}", level="ERROR")
            await self.set_state(
                "sensor.aimesh_speedtest_result",
                state="error",
                attributes={"error": str(e)},
            )
            return
        self.log("Speedtest triggered successfully", level="INFO")

        try:
            data = await get_speed_test_data(
                self.args["router_host"],
                self.args["router_username"],
                self.args["router_password"],
            )
        except Exception as e:
            self.log(f"Could not get speedtest data: {e}", level="ERROR")
            await self.set_state(
                "sensor.aimesh_speedtest_result",
                state="error",
                attributes={"error": str(e)},
            )
            return
        finally:
            self.check_in_progress = False

        speedtest_data = parse_speedtest_result(data)

        await self.set_state(
            "sensor.aimesh_speedtest_result",
            state=str(round(speedtest_data.download.megabits_per_second, 1)),
            attributes={
                "download_mbps": speedtest_data.download.megabits_per_second,
                "upload_mbps": speedtest_data.upload.megabits_per_second,
                "ping_latency": speedtest_data.ping.latency,
                "ping_jitter": speedtest_data.ping.jitter,
                "server": speedtest_data.server,
                "error": None,
                "unit_of_measurement": "Mbps",
            },
        )

        speed_issues = (
            speedtest_data.download.megabits_per_second
            < CONNECTION_SPEED * ISSUE_THRESHOLD
            or speedtest_data.upload.megabits_per_second
            < CONNECTION_SPEED * ISSUE_THRESHOLD
        )
        if speed_issues:
            message = f"Internet is experiencing slower speeds than usual,\ndownload: {speedtest_data.download.megabits_per_second}\nupload: {speedtest_data.upload.megabits_per_second}"
            if self.debug:
                self.log(message, level="INFO")
            elif self.notify_target:
                await self.notify(
                    message, title="Internet speed issue", name=self.notify_target
                )
