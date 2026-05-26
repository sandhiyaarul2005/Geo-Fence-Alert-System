# GNSS Based Tracking System with LTE SMS Alerting
## LTE-Based SMS Communication

### Role of LTE Module
The LTE module acts as a **cellular communication interface** that enables the system to send SMS messages directly over the mobile network without requiring internet connectivity.

The EC200 module communicates with the controller using **AT commands over serial interface**, allowing programmatic control of SMS functionality.

---

### SMS Workflow

1. **Initialize LTE Module**
   - The system communicates with the LTE modem using serial AT commands.
   - Basic initialization ensures the modem is responsive.

2. **Enable SMS Text Mode**
   ```bash
   AT+CMGF=1
