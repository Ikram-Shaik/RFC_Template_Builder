def juniper_l2(OG, A, Z, Test, Side):
    Side = Side.upper()

    if Side not in ["A", "Z"]:
        raise ValueError("Side must be A or Z")

    template = ["RFC Template:", "Original Config:"] + OG

    l2protocols = []
    A_end_config = []
    Z_end_config = []

    for line in template:
        if "set protocols l2circuit local-switching" in line:
            l2protocols.append(line)
        else:
            if "set interfaces " + A.split(".")[0] in line:
                A_end_config.append(line)
            elif "set interfaces " + Z.split(".")[0] in line:
                Z_end_config.append(line)

    if not l2protocols:
        raise ValueError("No L2 circuit local-switching configuration found")

    if not A_end_config:
        raise ValueError(f"A interface configuration not found: {A.split('.')[0]}")

    if not Z_end_config:
        raise ValueError(f"Z interface configuration not found: {Z.split('.')[0]}")

    empty = "--------------------------------------------"

    template.extend([
        empty,
        f"Test Head :{Test}",
        empty
    ])

    protocol = l2protocols[0].split()

    delete_protocol = "delete " + " ".join(
        protocol[1:protocol.index(A) + 1]
    )

    template.extend([
        delete_protocol,
        ""
    ])

    if Side == "A":
        modprotocols = l2protocols.copy()

        for i in range(len(Z_end_config)):
            Z_end_config[i] = Z_end_config[i].replace(
                Z.split(".")[0],
                Test
            )

        for i in range(len(modprotocols)):
            modprotocols[i] = modprotocols[i].replace(
                Z.split(".")[0],
                Test
            )

        template.extend(Z_end_config)
        template.append("")
        template.extend(modprotocols)

    elif Side == "Z":
        modprotocols = l2protocols.copy()

        for i in range(len(A_end_config)):
            A_end_config[i] = A_end_config[i].replace(
                A.split(".")[0],
                Test
            )

        for i in range(len(modprotocols)):
            modprotocols[i] = modprotocols[i].replace(
                A.split(".")[0],
                Test
            )

        template.extend(A_end_config)
        template.append("")
        template.extend(modprotocols)

    template.extend([
        "",
        empty,
        "",
        "Normalize :",
        ""
    ])

    if Side == "A":
        int_del = f"del interfaces {Test} unit {Z.split('.')[1]}"

        template.extend([
            delete_protocol,
            "",
            int_del,
            ""
        ])

    elif Side == "Z":
        int_del = f"del interfaces {Test} unit {A.split('.')[1]}"

        template.extend([
            delete_protocol.replace(A.split(".")[0], Test),
            "",
            int_del,
            ""
        ])

    template.extend(l2protocols)

    return "\n".join(template)