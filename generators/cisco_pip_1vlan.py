import re


def extract_interface_config(original_config, interface):
    lines = original_config.splitlines()

    interface_lines = []
    inside_interface = False

    for line in lines:
        stripped = line.strip()

        if stripped == f"interface {interface}":
            inside_interface = True
            interface_lines.append(line.rstrip())
            continue

        if inside_interface:
            if stripped == "!":
                interface_lines.append(line.rstrip())
                break

            interface_lines.append(line.rstrip())

    if not interface_lines:
        raise ValueError(f"Interface {interface} not found in Original Config.")

    return interface_lines


def extract_vlan(interface_lines):
    for line in interface_lines:
        match = re.search(r"encapsulation dot1q\s+(\d+)", line)

        if match:
            return match.group(1)

    raise ValueError("VLAN ID not found in Original Config.")


def extract_unit(interface):
    if "." not in interface:
        raise ValueError(
            f"Interface {interface} must contain a unit, for example .82"
        )

    return interface.rsplit(".", 1)[1]


def extract_test_interface(test_head):
    test_head = test_head.strip()

    if ":" in test_head:
        return test_head.split(":", 1)[1].strip()

    return test_head


def build_service_policy(speed):
    speed = str(speed).strip().lower().replace(" ", "")

    match = re.fullmatch(r"(\d+(?:\.\d+)?)(mbps|gbps)", speed)

    if not match:
        raise ValueError(
            "Circuit Speed must be a valid number with Mbps or Gbps."
        )

    value = float(match.group(1))
    unit = match.group(2)

    if unit == "mbps":
        speed_k = int(value * 1000)
    else:
        speed_k = int(value * 1000000)

    return f"EVCin_{speed_k}K"


def build_original_test_config(
    interface,
    vlan,
    service_policy
):
    return [
        f"interface {interface} l2transport",
        f" encapsulation dot1q {vlan}",
        f" rewrite ingress tag translate 1-to-1 dot1q {vlan} symmetric",
        f" service-policy input {service_policy}",
        "!"
    ]


def build_test_interface_config(
    test_interface,
    unit,
    vlan,
    service_policy
):
    return [
        f"int {test_interface}.{unit}  l2transport",
        f" encapsulation dot1q {vlan}",
        f" rewrite ingress tag translate 1-to-1 dot1q {vlan} symmetric",
        f" service-policy input {service_policy}",
        "!"
    ]


def build_xconnect_config(
    interface,
    test_interface,
    unit
):
    return [
        "l2vpn",
        " xconnect group LOCAL-SWITCH",
        "  p2p RFCTEST",
        f"   interface {interface}",
        f"   interface {test_interface}.{unit}",
        "  !",
        " !",
        "!"
    ]


def cisco_pip_1vlan(
    original_config,
    interface,
    test_head,
    speed
):
    original_config = original_config.strip()
    interface = interface.strip()
    test_head = test_head.strip()

    if not original_config:
        raise ValueError("Original Config is required.")

    if not interface:
        raise ValueError("Interface is required.")

    if not test_head:
        raise ValueError("Test Head is required.")

    interface_lines = extract_interface_config(
        original_config,
        interface
    )

    vlan = extract_vlan(interface_lines)
    unit = extract_unit(interface)

    test_interface = extract_test_interface(test_head)

    service_policy = build_service_policy(speed)

    original_test_config = build_original_test_config(
        interface,
        vlan,
        service_policy
    )

    test_interface_config = build_test_interface_config(
        test_interface,
        unit,
        vlan,
        service_policy
    )

    xconnect_config = build_xconnect_config(
        interface,
        test_interface,
        unit
    )

    original_interface_config = "\n".join(
        interface_lines
    )

    return (
        "RFC Template:\n\n"
        "Original Config:\n\n"
        f"{original_config}\n\n"
        "------------------------------------------------------------\n\n"
        f"Test Head : {test_head}\n\n"
        "------------------------------------------------------------\n\n"
        f"no interface {interface}\n\n\n"
        + "\n".join(original_test_config)
        + "\n"
        + "\n".join(test_interface_config)
        + "\n\n"
        + "\n".join(xconnect_config)
        + "\n\n"
        "------------------------------------------------------------\n\n"
        "Normalize:\n\n"
        "l2vpn\n"
        " xconnect group LOCAL-SWITCH\n"
        "  no p2p RFCTEST\n"
        "   !\n"
        " !\n"
        "!\n\n"
        f"no interface {interface}\n"
        f"no interface {test_interface}.{unit}\n\n\n"
        f"{original_interface_config}"
    )
