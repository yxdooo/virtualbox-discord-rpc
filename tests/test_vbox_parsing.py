from __future__ import annotations

from virtualbox_rpc.vbox import parse_running_vms, parse_vminfo


def test_parse_running_vms_empty():
    assert parse_running_vms("") == []
    assert parse_running_vms("\n   \n") == []


def test_parse_running_vms_single():
    output = '"kali-linux-2026.2" {e7aff680-294a-46b8-8744-57732aaaaad2}\n'
    assert parse_running_vms(output) == ["kali-linux-2026.2"]


def test_parse_running_vms_multiple():
    output = (
        '"Ubuntu 24.04 LTS" {11111111-2222-3333-4444-555555555555}\n'
        '"Windows 11 Pro" {aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee}\n'
    )
    assert parse_running_vms(output) == ["Ubuntu 24.04 LTS", "Windows 11 Pro"]


def test_parse_running_vms_malformed_lines():
    output = 'garbage line without quotes\n"ValidVM" {1234}\nanother invalid line\n'
    assert parse_running_vms(output) == ["ValidVM"]


def test_parse_vminfo_full():
    sample = """
name="debian-test"
ostype="Debian (64-bit)"
VMState="running"
memory=4096
cpus=4
"""
    info = parse_vminfo(sample)
    assert info.name == "debian-test"
    assert info.ostype == "Debian (64-bit)"
    assert info.state == "running"
    assert info.memory_mb == 4096
    assert info.cpus == 4
    assert info.specs == "4 vCPUs • 4.0 GB RAM"


def test_parse_vminfo_small_memory_single_cpu():
    sample = """
name="alpine"
ostype="Linux 2.6 / 3.x / 4.x / 5.x (64-bit)"
VMState="paused"
memory=512
cpus=1
"""
    info = parse_vminfo(sample)
    assert info.name == "alpine"
    assert info.state == "paused"
    assert info.specs == "1 vCPU • 512 MB RAM"


def test_parse_vminfo_missing_fields():
    info = parse_vminfo("")
    assert info.ostype == "Virtual Machine"
    assert info.state == "running"
    assert info.specs == ""
