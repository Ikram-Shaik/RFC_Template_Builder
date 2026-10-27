import streamlit as st

from generators.fujitsu_l2 import fujitsu_l2
from generators.juniper_l2 import juniper_l2
from generators.tellabs_l2 import tellabs_l2
from generators.juniper_pip_1vlan import juniper_pip_1vlan
from generators.juniper_pip_2vlan import juniper_pip_2vlan
from generators.cisco_pip_1vlan import cisco_pip_1vlan
from generators.cisco_pip_2vlan import cisco_pip_2vlan


st.set_page_config(
    page_title="RFC Template Builder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown(
    """
    <style>

    .stApp {
        background: #f7f9fc;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(
            135deg,
            #172554 0%,
            #1e3a8a 50%,
            #4338ca 100%
        );
        padding: 30px 38px;
        border-radius: 0 0 22px 22px;
        margin-bottom: 30px;
        box-shadow: 0 15px 35px rgba(30, 58, 138, 0.22);
    }

    .hero-title {
        color: #ffffff !important;
        font-size: 34px !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        margin: 0 !important;
    }

    .hero-icon {
        color: #fbbf24 !important;
        font-size: 38px !important;
        margin-right: 12px !important;
    }

    .hero-subtitle {
        color: #dbeafe !important;
        font-size: 15px !important;
        margin-top: 10px !important;
    }

    .section-title {
        color: #111827 !important;
        font-size: 21px !important;
        font-weight: 700 !important;
        margin-top: 4px !important;
        margin-bottom: 14px !important;
    }

    div[data-testid="stRadio"] > label {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stRadio"] label p {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-weight: 500 !important;
    }

    div[data-testid="stRadio"] label span {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stNumberInput"] label {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stSelectbox"] label p,
    div[data-testid="stTextInput"] label p,
    div[data-testid="stTextArea"] label p,
    div[data-testid="stNumberInput"] label p {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] * {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stNumberInput"] input {
        background-color: #ffffff !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 10px !important;
    }

    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #6b7280 !important;
        -webkit-text-fill-color: #6b7280 !important;
        opacity: 1 !important;
    }

    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
        caret-color: #111827 !important;
        font-family: Consolas, monospace !important;
        font-size: 13px !important;
    }

    div[data-testid="stNumberInput"] input {
        background-color: #ffffff !important;
        color: #111827 !important;
        caret-color: #111827 !important;
    }

    div[data-testid="stButton"] > button {
        background: #2563eb !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        min-height: 58px !important;
        width: 100% !important;
        padding: 0.8rem 1.4rem !important;
        font-size: 17px !important;
        font-weight: 600 !important;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.28) !important;
    }

    div[data-testid="stButton"] > button:hover {
        background: #1d4ed8 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        box-shadow: 0 12px 28px rgba(37, 99, 235, 0.34) !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    div[data-testid="stAlert"] p {
        font-weight: 500 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            <span class="hero-icon">⚡</span>
            RFC Template Builder
        </div>
        <div class="hero-subtitle">
            Network configuration automation for faster and consistent RFC generation
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="section-title">⚙️ Device Configuration</div>',
    unsafe_allow_html=True
)


layer = st.radio(
    "Select Layer",
    [
        "Layer 2",
        "PIP",
        "PWE"
    ],
    horizontal=True
)


if layer == "Layer 2":

    left_col, right_col = st.columns(
        [0.9, 1.8],
        gap="large"
    )

    with left_col:

        device = st.selectbox(
            "Device Type",
            [
                "Juniper",
                "Cisco",
                "Tellabs",
                "Fujitsu"
            ]
        )

        interface_a = st.text_input(
            "A End Interface",
            placeholder="Enter A End Interface"
        )

        interface_z = st.text_input(
            "Z End Interface",
            placeholder="Enter Z End Interface"
        )

        test_head = st.text_input(
            "Test Head Port",
            placeholder="Enter Test Head Port"
        )

        side = st.selectbox(
            "Test Side",
            [
                "A",
                "Z"
            ]
        )

    with right_col:

        st.markdown(
            '<div class="section-title">📋 Original Configuration</div>',
            unsafe_allow_html=True
        )

        original_config = st.text_area(
            "Original Config",
            placeholder="Paste Original Config here...",
            height=390,
            label_visibility="collapsed"
        )

        if st.button(
            "⚡ Generate RFC Template",
            key="layer2_generate"
        ):

            try:

                if not interface_a.strip():
                    raise ValueError(
                        "A End Interface is required."
                    )

                if not interface_z.strip():
                    raise ValueError(
                        "Z End Interface is required."
                    )

                if not test_head.strip():
                    raise ValueError(
                        "Test Head Port is required."
                    )

                if not original_config.strip():
                    raise ValueError(
                        "Original Config is required."
                    )

                if device == "Juniper":

                    result = juniper_l2(
                        original_config,
                        interface_a,
                        interface_z,
                        test_head,
                        side
                    )

                    st.success(
                        "Juniper L2 RFC Template generated successfully."
                    )

                elif device == "Tellabs":

                    result = tellabs_l2(
                        original_config,
                        interface_a,
                        interface_z,
                        test_head,
                        side
                    )

                    st.success(
                        "Tellabs L2 RFC Template generated successfully."
                    )

                elif device == "Fujitsu":

                    result = fujitsu_l2(
                        original_config,
                        interface_a,
                        interface_z,
                        test_head,
                        side
                    )

                    st.success(
                        "Fujitsu L2 RFC Template generated successfully."
                    )

                elif device == "Cisco":

                    st.warning(
                        "Cisco L2 generator is not implemented yet."
                    )

                    result = None

                if result:

                    st.markdown(
                        '<div class="section-title">📄 Generated RFC</div>',
                        unsafe_allow_html=True
                    )

                    st.text_area(
                        "Generated RFC Template",
                        result,
                        height=800,
                        label_visibility="collapsed"
                    )

            except Exception as e:

                st.error(str(e))


elif layer == "PIP":

    st.markdown(
        '<div class="section-title">⚙️ PIP Configuration</div>',
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns(
        [0.9, 1.8],
        gap="large"
    )

    with left_col:

        pip_device = st.selectbox(
            "Device Type",
            [
                "Juniper",
                "Cisco"
            ]
        )

        pip_vlan_type = st.selectbox(
            "VLAN Type",
            [
                "Single VLAN",
                "2 VLANs"
            ]
        )

        interface = st.text_input(
            "Interface",
            placeholder="Enter Interface"
        )

        test_head = st.text_input(
            "Test Head Port",
            placeholder="Enter Test Head Port"
        )

        speed_col1, speed_col2 = st.columns(
            [1.5, 1]
        )

        with speed_col1:

            circuit_speed_value = st.number_input(
                "Circuit Speed",
                min_value=1,
                step=1,
                value=10
            )

        with speed_col2:

            circuit_speed_unit = st.selectbox(
                "Unit",
                [
                    "Mbps",
                    "Gbps"
                ]
            )

        circuit_speed = (
            f"{circuit_speed_value} "
            f"{circuit_speed_unit}"
        )

    with right_col:

        st.markdown(
            '<div class="section-title">📋 Original Configuration</div>',
            unsafe_allow_html=True
        )

        original_config = st.text_area(
            "Original Config",
            placeholder="Paste Original Config here...",
            height=390,
            label_visibility="collapsed"
        )

        if st.button(
            "⚡ Generate RFC Template",
            key="pip_generate"
        ):

            try:

                if not interface.strip():
                    raise ValueError(
                        "Interface is required."
                    )

                if not test_head.strip():
                    raise ValueError(
                        "Test Head Port is required."
                    )

                if not original_config.strip():
                    raise ValueError(
                        "Original Config is required."
                    )

                if (
                    pip_device == "Juniper"
                    and pip_vlan_type == "Single VLAN"
                ):

                    result = juniper_pip_1vlan(
                        original_config,
                        interface,
                        test_head,
                        circuit_speed
                    )

                    st.success(
                        "Juniper PIP 1 VLAN RFC Template generated successfully."
                    )

                elif (
                    pip_device == "Juniper"
                    and pip_vlan_type == "2 VLANs"
                ):

                    result = juniper_pip_2vlan(
                        original_config,
                        interface,
                        test_head,
                        circuit_speed
                    )

                    st.success(
                        "Juniper PIP 2 VLAN RFC Template generated successfully."
                    )

                elif (
                    pip_device == "Cisco"
                    and pip_vlan_type == "Single VLAN"
                ):

                    result = cisco_pip_1vlan(
                        original_config,
                        interface,
                        test_head,
                        circuit_speed
                    )

                    st.success(
                        "Cisco PIP 1 VLAN RFC Template generated successfully."
                    )

                elif (
                    pip_device == "Cisco"
                    and pip_vlan_type == "2 VLANs"
                ):

                    result = cisco_pip_2vlan(
                        original_config,
                        interface,
                        test_head,
                        circuit_speed
                    )

                    st.success(
                        "Cisco PIP 2 VLAN RFC Template generated successfully."
                    )

                if result:

                    st.markdown(
                        '<div class="section-title">📄 Generated RFC</div>',
                        unsafe_allow_html=True
                    )

                    st.text_area(
                        "Generated RFC Template",
                        result,
                        height=800,
                        label_visibility="collapsed"
                    )

            except Exception as e:

                st.error(str(e))


elif layer == "PWE":

    st.markdown(
        '<div class="section-title">⚙️ PWE Configuration</div>',
        unsafe_allow_html=True
    )

    st.info(
        "PWE RFC Template generator will be added here."
    )