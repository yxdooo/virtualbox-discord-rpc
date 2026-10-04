from __future__ import annotations

from virtualbox_rpc.client import build_presence_payload
from virtualbox_rpc.config import Config


def test_build_presence_no_vms():
    cfg = Config()
    payload = build_presence_payload(
        running_vms=[],
        vm_specs_map={},
        manager_start_time=1000,
        vm_start_times={},
        config=cfg,
    )
    assert payload is not None
    assert payload["details"] == "VirtualBox Manager"
    assert payload["state"] == "Configuring Virtual Machines"
    assert payload["start"] == 1000


def test_build_presence_single_running_vm():
    cfg = Config()
    specs = {
        "kali": {
            "ostype": "Debian (64-bit)",
            "specs": "4 vCPUs • 4.0 GB RAM",
            "state": "running",
        }
    }
    payload = build_presence_payload(
        running_vms=["kali"],
        vm_specs_map=specs,
        manager_start_time=1000,
        vm_start_times={"kali": 2000},
        config=cfg,
    )
    assert payload is not None
    assert payload["details"] == "Running: kali"
    assert "Debian (64-bit)" in payload["state"]
    assert "4 vCPUs" in payload["state"]
    assert payload["start"] == 2000


def test_build_presence_single_paused_vm():
    cfg = Config()
    specs = {
        "ubuntu": {
            "ostype": "Ubuntu (64-bit)",
            "specs": "2 vCPUs • 2.0 GB RAM",
            "state": "paused",
        }
    }
    payload = build_presence_payload(
        running_vms=["ubuntu"],
        vm_specs_map=specs,
        manager_start_time=1000,
        vm_start_times={"ubuntu": 2000},
        config=cfg,
    )
    assert payload is not None
    assert payload["details"] == "Running: ubuntu"
    assert "Paused" in payload["state"]


def test_build_presence_multiple_vms():
    cfg = Config()
    payload = build_presence_payload(
        running_vms=["vm1", "vm2"],
        vm_specs_map={},
        manager_start_time=1000,
        vm_start_times={"vm1": 1500, "vm2": 1800},
        config=cfg,
    )
    assert payload is not None
    assert payload["details"] == "Running 2 Virtual Machines"
    assert "vm1, vm2" in payload["state"]
    assert payload["start"] == 1500


def test_build_presence_hardware_specs_disabled():
    cfg = Config(show_hardware_specs=False)
    specs = {
        "kali": {
            "ostype": "Debian (64-bit)",
            "specs": "4 vCPUs • 4.0 GB RAM",
            "state": "running",
        }
    }
    payload = build_presence_payload(
        running_vms=["kali"],
        vm_specs_map=specs,
        manager_start_time=1000,
        vm_start_times={"kali": 2000},
        config=cfg,
    )
    assert payload is not None
    assert payload["state"] == "Debian (64-bit)"


def test_build_presence_privacy_mode():
    cfg = Config()
    cfg.privacy.hide_vm_name = True
    cfg.privacy.hide_hardware_specs = True

    specs = {
        "sensitive_vm": {
            "ostype": "Debian (64-bit)",
            "specs": "16 vCPUs • 32.0 GB RAM",
            "state": "running",
        }
    }
    payload = build_presence_payload(
        running_vms=["sensitive_vm"],
        vm_specs_map=specs,
        manager_start_time=1000,
        vm_start_times={"sensitive_vm": 2000},
        config=cfg,
    )
    assert payload is not None
    assert payload["details"] == "Running: Virtual Machine"
    assert payload["state"] == "Debian (64-bit)"
    assert "16 vCPUs" not in payload["state"]

    # Multiple VMs with privacy
    payload_multi = build_presence_payload(
        running_vms=["sensitive_1", "sensitive_2"],
        vm_specs_map={},
        manager_start_time=1000,
        vm_start_times={},
        config=cfg,
    )
    assert payload_multi is not None
    assert payload_multi["state"] == "Multiple instances active"


def test_build_presence_vm_overrides():
    from virtualbox_rpc.config import VmOverride

    cfg = Config()
    cfg.vm_overrides = {"lab_vm": VmOverride(display_name="Security Sandbox", icon="arch")}

    specs = {
        "lab_vm": {
            "ostype": "Linux (64-bit)",
            "specs": "2 vCPUs • 4.0 GB RAM",
            "state": "running",
        }
    }
    payload = build_presence_payload(
        running_vms=["lab_vm"],
        vm_specs_map=specs,
        manager_start_time=1000,
        vm_start_times={"lab_vm": 2000},
        config=cfg,
    )
    assert payload is not None
    assert payload["details"] == "Running: Security Sandbox"
    from virtualbox_rpc.config import OS_ICONS

    assert payload["small_image"] == OS_ICONS["arch"]
