import re


def extract_circuit_config(original_config):
    lines = original_config.splitlines()

    start = None
    end = None

    for i, line in enumerate(lines):
        if re.search(r'\bexit all\b', line, re.IGNORECASE):
            for j in range(i + 1, len(lines)):
                if re.search(
                    r'enable\s+config\s+ckt\s+name\s+',
                    lines[j],
                    re.IGNORECASE
                ):
                    start = i
                    break
            if start is not None:
                break

    if start is None:
        raise ValueError("Tellabs circuit configuration not found")

    for i in range(start, len(lines)):
        if re.match(r'\s*admin\s+enable\s*$', lines[i], re.IGNORECASE):
            end = i
            break

    if end is None:
        raise ValueError("Tellabs circuit ending 'admin enable' not found")

    return lines[start:end + 1]


def extract_circuit_name(config_lines):
    pattern = re.compile(
        r'enable\s+config\s+ckt\s+name\s+"?([^"\s]+)"?\s+type\s+vlan',
        re.IGNORECASE
    )

    for line in config_lines:
        match = pattern.search(line)
        if match:
            return match.group(1)

    raise ValueError("Tellabs circuit name not found")


def replace_interface(config_lines, original_interface, test_interface):
    result = []
    replaced = False

    for line in config_lines:
        if re.search(
            rf'^\s*interface\s+{re.escape(original_interface)}\s*$',
            line,
            re.IGNORECASE
        ):
            line = re.sub(
                rf'(\binterface\s+){re.escape(original_interface)}\b',
                rf'\g<1>{test_interface}',
                line,
                flags=re.IGNORECASE
            )
            replaced = True

        result.append(line)

    if not replaced:
        raise ValueError(
            f"Interface {original_interface} not found in Tellabs configuration"
        )

    return result


def build_test_config(
    original_lines,
    circuit_name,
    original_interface,
    test_interface
):
    config = original_lines.copy()

    config = replace_interface(
        config,
        original_interface,
        test_interface
    )

    result = []

    for line in config:
        line = re.sub(
            rf'(enable\s+config\s+ckt\s+name\s+)"?{re.escape(circuit_name)}"?',
            r'\1"RFC_TESTING"',
            line,
            flags=re.IGNORECASE
        )

        line = re.sub(
            rf'(\bdescription\s+)"?{re.escape(circuit_name)}"?',
            r'\1"RFC_TESTING"',
            line,
            flags=re.IGNORECASE
        )

        result.append(line)

    return result


def tellabs_l2(original_config, A, Z, Test, Side):
    Side = Side.upper()

    if Side not in ["A", "Z"]:
        raise ValueError("Side must be A or Z")

    if not A or not Z or not Test:
        raise ValueError("A-End, Z-End and Test Head are required")

    original_lines = extract_circuit_config(original_config)

    circuit_name = extract_circuit_name(original_lines)

    interfaces = [
        line.strip().split(maxsplit=1)[1]
        for line in original_lines
        if re.match(r'\s*interface\s+\S+', line, re.IGNORECASE)
    ]

    if A not in interfaces:
        raise ValueError(f"A interface not found: {A}")

    if Z not in interfaces:
        raise ValueError(f"Z interface not found: {Z}")

    if Side == "A":
        selected_interface = Z
    else:
        selected_interface = A

    test_config = build_test_config(
        original_lines,
        circuit_name,
        selected_interface,
        Test
    )

    original_config_text = "\n".join(original_lines)
    test_config_text = "\n".join(test_config)

    delete_original = (
        f"enable\n"
        f'config ckt name {circuit_name} admin disable\n'
        f'config no ckt name {circuit_name}'
    )

    delete_test = (
        'enable\n'
        'config ckt name "RFC_TESTING" admin disable\n'
        'config no ckt name "RFC_TESTING"'
    )

    return (
        "RFC Template:\n\n"
        "Original Config:\n"
        f"{original_config_text}\n\n"
        "---------------------------\n"
        f"Test Head : {Test}\n"
        "--------------------------\n\n"
        f"{delete_original}\n\n"
        "exit all\n"
        "enable\n"
        f"{test_config_text}\n\n"
        "-----------------------------\n\n"
        "Normalize :\n\n"
        f"{delete_test}\n\n"
        "exit all\n"
        "enable\n"
        f"{original_config_text}"
    )