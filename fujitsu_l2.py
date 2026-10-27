import re


def parse_endpoints(config):
    data = config

    data = re.sub(
        r'HDTD\s+PFL',
        'HDTDPFL',
        data,
        flags=re.IGNORECASE
    )

    data = re.sub(
        r'(\d+)\s*-\s*(\d+)',
        r'\1-\2',
        data
    )

    data = re.sub(r'\s+', ' ', data)

    pattern = re.compile(
        r'(\d+-\d+-\d+-\d+):TFP:(.*?)(?=\d+-\d+-\d+-\d+:TFP:|$)',
        re.IGNORECASE
    )

    endpoints = {}

    for match in pattern.finditer(data):
        interface = match.group(1)
        block = match.group(2)

        fields = {}

        field_names = [
            "TSG",
            "SDT",
            "IBWPFL",
            "EBWPFL",
            "IPBPFL",
            "HDTDPFL",
            "OUTERVID",
            "PMHISTORY"
        ]

        for field in field_names:
            results = re.findall(
                rf'{field}\s*=\s*([^,\s]+)',
                block,
                re.IGNORECASE
            )

            if results:
                fields[field] = results[-1]

        endpoints[interface] = fields

    return endpoints


def create_ent(interface, config):
    fields = [
        "TSG",
        "SDT",
        "IBWPFL",
        "EBWPFL",
        "IPBPFL",
        "HDTDPFL",
        "OUTERVID",
        "PMHISTORY"
    ]

    values = []

    for field in fields:
        if field not in config:
            raise ValueError(f"{field} not found")

        values.append(f"{field}={config[field]}")

    return (
        f"ENT-FP::{interface}:CTAG::TFP:"
        + ",".join(values)
        + ";"
    )


def create_test_interface(interface, test_head):
    test_head = test_head.replace(".", "-")
    last_component = interface.split("-")[-1]
    return f"{test_head}-{last_component}"


def fujitsu_l2(original_config, A, Z, Test, Side):
    Side = Side.upper()

    endpoints = parse_endpoints(original_config)

    if A not in endpoints:
        raise ValueError(f"A interface {A} not found")

    if Z not in endpoints:
        raise ValueError(f"Z interface {Z} not found")

    if Side == "A":
        selected_interface = Z
        selected_config = endpoints[Z]
    elif Side == "Z":
        selected_interface = A
        selected_config = endpoints[A]
    else:
        raise ValueError("Side must be A or Z")

    test_interface = create_test_interface(
        selected_interface,
        Test
    )

    test_ent = create_ent(
        test_interface,
        selected_config
    )

    original_ent = create_ent(
        selected_interface,
        selected_config
    )

    return (
        "RFC Template:\n\n"
        "Original Config:\n"
        f"{original_config}\n\n"
        "--------------------------------------------\n"
        f"Test Head : {Test}\n"
        "--------------------------------------------\n\n"
        f"DLT-FP::{selected_interface}:\n\n"
        f"{test_ent}\n\n"
        "--------------------------------------------\n"
        "Normalization :\n\n"
        f"DLT-FP::{test_interface}:\n\n"
        f"{original_ent}"
    )