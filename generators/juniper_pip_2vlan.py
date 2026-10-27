import re


def extract_interface_config(original_config, interface):
    base_interface, unit = interface.rsplit(".", 1)

    interface_lines = []
    routing_lines = []
    routing_interface_lines = []

    for line in original_config.splitlines():
        line = line.strip()

        if re.search(
            rf"^set interfaces {re.escape(base_interface)} unit {re.escape(unit)}\b",
            line
        ):
            interface_lines.append(line)

        if re.search(
            rf"^set routing-instances \S+ .*interface {re.escape(interface)}(?:\s+.*)?$",
            line
        ):
            routing_lines.append(line)

        if re.search(
            rf"^set routing-instances \S+ interface {re.escape(interface)}$",
            line
        ):
            routing_interface_lines.append(line)

    if not interface_lines:
        raise ValueError(
            f"Interface {interface} not found in Original Config."
        )

    if not routing_lines:
        raise ValueError(
            f"Routing-instance configuration for {interface} not found."
        )

    if not routing_interface_lines:
        raise ValueError(
            f"Routing-instance interface configuration for {interface} not found."
        )

    return (
        base_interface,
        unit,
        interface_lines,
        routing_lines,
        routing_interface_lines
    )


def extract_vlan_tags(interface_lines):
    outer_vlan = None
    inner_vlan = None

    for line in interface_lines:
        outer_match = re.search(
            r"\bvlan-tags\s+outer\s+(\S+)",
            line
        )

        inner_match = re.search(
            r"\bvlan-tags\s+inner\s+(\S+)",
            line
        )

        if outer_match:
            outer_vlan = outer_match.group(1)

        if inner_match:
            inner_vlan = inner_match.group(1)

    if not outer_vlan:
        raise ValueError("Outer VLAN not found in interface configuration.")

    if not inner_vlan:
        raise ValueError("Inner VLAN not found in interface configuration.")

    return outer_vlan, inner_vlan


def extract_description(interface_lines):
    for line in interface_lines:
        if re.search(r"\sdescription\s+", line):
            return line

    raise ValueError("Interface description not found.")


def build_test_filter(speed):
    speed = speed.strip().lower().replace(" ", "")

    match = re.fullmatch(r"(\d+)(mbps|gbps)", speed)

    if not match:
        raise ValueError(
            "Circuit Speed must be a valid number with Mbps or Gbps."
        )

    number = match.group(1)
    unit = match.group(2)

    if unit == "mbps":
        return f"EVPL_{number}mEVC_Filter"

    return f"EVPL_{number}gEVC_Filter"


def extract_test_interface(test_head):
    test_head = test_head.strip()

    if ":" in test_head:
        return test_head.split(":", 1)[1].strip()

    return test_head


def juniper_pip_2vlan(
    original_config,
    interface,
    test_head,
    speed
):
    interface = interface.strip()
    test_head = test_head.strip()

    if not interface:
        raise ValueError("Interface is required.")

    if not test_head:
        raise ValueError("Test Head is required.")

    (
        base_interface,
        unit,
        interface_lines,
        routing_lines,
        routing_interface_lines
    ) = extract_interface_config(
        original_config,
        interface
    )

    outer_vlan, inner_vlan = extract_vlan_tags(
        interface_lines
    )

    description = extract_description(
        interface_lines
    )

    test_interface = extract_test_interface(
        test_head
    )

    test_filter = build_test_filter(
        speed
    )

    delete_routing = []

    for line in routing_interface_lines:
        delete_routing.append(
            f"delete {line[len('set '):]}"
        )

    test_config = [
        description,
        f"set interfaces {base_interface} unit {unit} encapsulation vlan-ccc",
        f"set interfaces {base_interface} unit {unit} vlan-tags outer {outer_vlan}",
        f"set interfaces {base_interface} unit {unit} vlan-tags inner {inner_vlan}",
        f"set interfaces {base_interface} unit {unit} input-vlan-map pop-swap inner-vlan-id {inner_vlan}",
        f"set interfaces {base_interface} unit {unit} output-vlan-map swap-push",
        f"set interfaces {base_interface} unit {unit} family ccc filter input {test_filter}",
        "",
        f"set interfaces {test_interface} unit {unit} encapsulation vlan-ccc",
        f"set interfaces {test_interface} unit {unit} vlan-id {inner_vlan}",
        f"set interfaces {test_interface} unit {unit} output-vlan-map swap",
        f"set interfaces {test_interface} unit {unit} family ccc filter input {test_filter}",
        "",
        f"set protocols l2circuit local-switching interface {test_interface}.{unit} end-interface interface {interface}",
        f"set protocols l2circuit local-switching interface {test_interface}.{unit} description RFCTEST",
        f"set protocols l2circuit local-switching interface {test_interface}.{unit} ignore-mtu-mismatch"
    ]

    delete_original_interface = (
        f"delete interfaces {base_interface} unit {unit}"
    )

    delete_test_interface = (
        f"delete interfaces {test_interface} unit {unit}"
    )

    delete_l2circuit = (
        f"delete protocols l2circuit local-switching "
        f"interface {test_interface}.{unit}"
    )

    original_config_lines = [
        line.rstrip()
        for line in original_config.splitlines()
    ]

    return (
        "RFC Template:\n\n"
        "Original Config ::\n\n"
        + "\n".join(original_config_lines)
        + "\n\n"
        "------------------------------------------------------------\n\n"
        f"Test Head: {test_head}\n\n"
        "------------------------------------------------------------\n\n"
        + "\n".join(delete_routing)
        + "\n\n"
        + delete_original_interface
        + "\n\n"
        + "\n".join(test_config)
        + "\n\n"
        "-----------------------\n\n"
        "Normalize :\n\n"
        + delete_original_interface
        + "\n"
        + delete_test_interface
        + "\n"
        + delete_l2circuit
        + "\n\n"
        + "\n".join(routing_interface_lines)
        + "\n\n"
        + "\n".join(interface_lines)
    )