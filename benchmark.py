
AUTOMOTIVE_PROMPTS = [
    # DTC Codes
    {"id": 1, "category": "DTC", "prompt": "Explain the diagnostic trouble code P0300 and list common causes for a 2018 Toyota Camry."},
    {"id": 2, "category": "DTC", "prompt": "What does DTC P0420 signify, and how can a technician verify if the catalytic converter is actually failing?"},
    {"id": 3, "category": "DTC", "prompt": "Analyze the possible causes for a U0100 code in a modern vehicle communication network."},
    {"id": 4, "category": "DTC", "prompt": "Explain the difference between P0171 and P0174 codes. What common component failure causes both?"},
    {"id": 5, "category": "DTC", "prompt": "What are the specific conditions required to set a P0442 EVAP leak code?"},
    {"id": 6, "category": "DTC", "prompt": "Describe the diagnostic steps for a P0A80 code in a hybrid vehicle battery pack."},
    {"id": 7, "category": "DTC", "prompt": "Explain the P0507 code related to Idle Control System RPM Higher Than Expected."},
    {"id": 8, "category": "DTC", "prompt": "What does a P0700 code indicate in an automatic transmission system?"},
    {"id": 9, "category": "DTC", "prompt": "Detail the troubleshooting process for a P0121 Throttle Position Sensor circuit range/performance problem."},
    {"id": 10, "category": "DTC", "prompt": "Explain the significance of a P2181 Cooling System Performance code."},

    # Sensor Specifications
    {"id": 11, "category": "Sensors", "prompt": "What is the typical voltage range for a 3-wire Hall Effect crankshaft position sensor?"},
    {"id": 12, "category": "Sensors", "prompt": "Describe the resistance characteristics of a standard NTC coolant temperature sensor as temperature increases."},
    {"id": 13, "category": "Sensors", "prompt": "Explain how a wideband oxygen sensor (UEGO) differs from a conventional Zirconia oxygen sensor in terms of signal output."},
    {"id": 14, "category": "Sensors", "prompt": "What are the typical operating parameters and pinout for a Bosch BMP280 manifold absolute pressure sensor used in automotive applications?"},
    {"id": 15, "category": "Sensors", "prompt": "How does a piezo-electric knock sensor generate a signal, and what frequency range does it typically monitor?"},
    {"id": 16, "category": "Sensors", "prompt": "Describe the function and typical output signal of a Mass Air Flow (MAF) sensor (Hot Wire type)."},
    {"id": 17, "category": "Sensors", "prompt": "What are the common failure modes of a Wheel Speed Sensor (WSS) in an ABS system?"},
    {"id": 18, "category": "Sensors", "prompt": "Explain the operation of an Accelerator Pedal Position (APP) sensor and why it typically uses two or three redundant signals."},
    {"id": 19, "category": "Sensors", "prompt": "Detail the specifications for a typical Fuel Rail Pressure (FRP) sensor in a common rail diesel engine."},
    {"id": 20, "category": "Sensors", "prompt": "What is the difference between an active and passive wheel speed sensor?"},

    # Automotive Standards
    {"id": 21, "category": "Standards", "prompt": "Explain the ASIL levels (A to D) defined in ISO 26262 and their implications for automotive software development."},
    {"id": 22, "category": "Standards", "prompt": "Describe the structure of an AUTOSAR (AUTomotive Open System ARchitecture) software component."},
    {"id": 23, "category": "Standards", "prompt": "What are the main differences between CAN 2.0B and CAN FD protocols?"},
    {"id": 24, "category": "Standards", "prompt": "Summarize the SAE J1939 standard's approach to Parameter Group Numbers (PGN) and Suspect Parameter Numbers (SPN)."},
    {"id": 25, "category": "Standards", "prompt": "Explain the requirements for Cybersecurity in vehicles as defined by ISO/SAE 21434."},
    {"id": 26, "category": "Standards", "prompt": "What is the Unified Diagnostic Services (UDS) protocol (ISO 14229) and list 5 common service IDs."},
    {"id": 27, "category": "Standards", "prompt": "Describe the LIN (Local Interconnect Network) bus architecture and its typical use cases in a vehicle."},
    {"id": 28, "category": "Standards", "prompt": "Explain the FlexRay protocol and why it is used in safety-critical applications like X-by-wire."},
    {"id": 29, "category": "Standards", "prompt": "What is the purpose of the OBD-II (On-Board Diagnostics) standard, and what are the mandatory monitors?"},
    {"id": 30, "category": "Standards", "prompt": "Describe the ISO 15765-2 (DoCAN) transport protocol layer."},

    # Technical Troubleshooting
    {"id": 31, "category": "Troubleshooting", "prompt": "A vehicle has a 'crank but no start' condition. List the top 5 diagnostic steps to isolate the issue."},
    {"id": 32, "category": "Troubleshooting", "prompt": "Diagnose a condition where a car pulls to the right only during braking. What are the most likely mechanical failures?"},
    {"id": 33, "category": "Troubleshooting", "prompt": "Explain why an engine might experience a 'stumble' under heavy load but idle perfectly fine."},
    {"id": 34, "category": "Troubleshooting", "prompt": "How do you diagnose a parasitic battery drain in a modern vehicle with multiple electronic control modules?"},
    {"id": 35, "category": "Troubleshooting", "prompt": "Describe the symptoms of a failing head gasket and the tests used to confirm it."},
    {"id": 36, "category": "Troubleshooting", "prompt": "A customer complains of a high-pitched squeal that changes with engine RPM. How do you distinguish between a belt issue and an alternator bearing?"},
    {"id": 37, "category": "Troubleshooting", "prompt": "Diagnose a 'spongy' brake pedal after a brake pad replacement. What went wrong?"},
    {"id": 38, "category": "Troubleshooting", "prompt": "What causes 'blue smoke' from the exhaust during cold starts vs. during acceleration?"},
    {"id": 39, "category": "Troubleshooting", "prompt": "How do you troubleshoot an intermittent 'no communication' issue with the Transmission Control Module (TCM)?"},
    {"id": 40, "category": "Troubleshooting", "prompt": "Explain the diagnostic process for a turbocharger underboost condition."},

    # Engineering Concepts
    {"id": 41, "category": "Concepts", "prompt": "Explain the operation of a Regenerative Braking system in an Electric Vehicle."},
    {"id": 42, "category": "Concepts", "prompt": "Describe the thermal management strategies used for Lithium-ion battery packs in EVs."},
    {"id": 43, "category": "Concepts", "prompt": "What is a Dual-Clutch Transmission (DCT), and how does it provide faster gear shifts than a traditional automatic?"},
    {"id": 44, "category": "Concepts", "prompt": "Explain the difference between Atkinson cycle and Otto cycle engines. Why is the Atkinson cycle preferred in hybrids?"},
    {"id": 45, "category": "Concepts", "prompt": "Describe the components and logic behind an Adaptive Cruise Control (ACC) system."},
    {"id": 46, "category": "Concepts", "prompt": "What is the role of a Battery Management System (BMS) in balancing cell voltages?"},
    {"id": 47, "category": "Concepts", "prompt": "Explain the concept of 'Hardware-in-the-Loop' (HiL) testing in automotive ECU development."},
    {"id": 48, "category": "Concepts", "prompt": "Describe how Electronic Stability Control (ESC) uses individual wheel braking to prevent a skid."},
    {"id": 49, "category": "Concepts", "prompt": "What are the advantages and disadvantages of 48V Mild Hybrid systems compared to full hybrids?"},
    {"id": 50, "category": "Concepts", "prompt": "Explain the working principle of a Variable Geometry Turbocharger (VGT)."}
]
