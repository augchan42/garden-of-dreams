#!/usr/bin/env python3
"""Run the Android Keystore fixtures only in the dedicated identity test package."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

PACKAGE = "ai.eightbitoracle.garden.identity.tests"
RUNNER = "androidx.test.runner.AndroidJUnitRunner"
TEST_CLASS = "ai.eightbitoracle.garden.identity.RecordsSessionStoreTest"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-report", type=Path, required=True)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--sdk", type=Path, default=Path.home() / "Library/Android/sdk")
    args = parser.parse_args()
    report = {
        "status": "running", "serial": args.serial, "package": PACKAGE,
        "scope": "Dedicated-package Android Keystore persistence and corruption tests. No Garden activity, Google chooser, server request, account session or frame profiling.",
        "phases": [],
    }

    def persist():
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")

    def run(command, timeout=180):
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        report["phases"].append({"command": command, "exit_code": result.returncode,
                                  "stdout": result.stdout, "stderr": result.stderr})
        persist()
        if result.returncode:
            raise RuntimeError("Command failed: " + command[0])
        return result.stdout

    try:
        build = json.loads(args.build_report.read_text())
        if build.get("status") != "compiled" or build.get("exit_code") != 0:
            raise ValueError("A successful current build report is required")
        artifact = build["device_test_apk"]
        apk = Path(artifact["path"])
        digest = hashlib.sha256(apk.read_bytes()).hexdigest()
        if artifact["package"] != PACKAGE or digest != artifact["sha256"]:
            raise ValueError("Test APK package or digest does not match the build")
        report["apk_sha256"] = digest
        report["build_report_sha256"] = hashlib.sha256(args.build_report.read_bytes()).hexdigest()
        aapt = args.sdk / "build-tools/36.1.0/aapt"
        manifest = run([str(aapt), "dump", "xmltree", str(apk), "AndroidManifest.xml"])
        # Check both the owning app and target before any install or test cleanup.
        for field, value in (("package", PACKAGE), ("android:targetPackage", PACKAGE),
                             ("android:name", RUNNER)):
            pattern = re.escape(field) + r'(?:\([^\n]*?\))?="' + re.escape(value) + '"'
            if not re.search(pattern, manifest):
                raise ValueError("Unexpected instrumentation manifest: " + field)
        adb = str(args.sdk / "platform-tools/adb")
        device = [adb, "-s", args.serial]
        if run(device + ["get-state"]).strip() != "device":
            raise RuntimeError("Selected test device is not authorized")
        if "Success" not in run(device + ["install", "-r", "-t", str(apk)]):
            raise RuntimeError("Test APK installation was not confirmed")
        installed = run(device + ["shell", "pm", "path", PACKAGE]).strip().splitlines()
        if len(installed) != 1 or not installed[0].startswith("package:/data/app/"):
            raise RuntimeError("Expected one installed test APK")
        remote = installed[0][len("package:"):]
        result = subprocess.run(device + ["exec-out", "cat", remote], capture_output=True, timeout=180)
        installed_digest = hashlib.sha256(result.stdout).hexdigest()
        report["installed_apk_sha256"] = installed_digest
        if result.returncode or installed_digest != digest:
            raise RuntimeError("Installed APK differs from the tested build")
        output = run(device + ["shell", "am", "instrument", "-r", "-w", "-e", "class",
                               TEST_CLASS, PACKAGE + "/" + RUNNER])
        if not re.search(r"OK \(11 tests\)", output) or "INSTRUMENTATION_CODE: -1" not in output:
            raise RuntimeError("Eleven passing storage tests were not confirmed")
        if output.count("INSTRUMENTATION_STATUS_CODE: 0") != 11:
            raise RuntimeError("Unexpected completed-test count")
        report["status"] = "passed"
        report["tests_passed"] = 11
    except Exception as failure:
        report["status"] = "failed"
        report["error"] = str(failure)
        persist()
        raise
    persist()
    print(json.dumps({key: report[key] for key in ("status", "tests_passed", "apk_sha256", "installed_apk_sha256")}, indent=2))


if __name__ == "__main__":
    main()
