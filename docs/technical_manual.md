# TECHNICAL MAINTENANCE AND TROUBLESHOOTING MANUAL
**Document Code:** MAN-IND-2015-V4 · **Standard:** ISO 13374

---

## SECTION 1: GENERAL SAFETY PROTOCOL (LOTO - Lockout / Tagout)
**Page 4 · Mandatory Workshop Safety**
Before performing maintenance on any machine (`model1`, `model2`, `model3`, `model4`):
1. **Power Isolation (LOTO):** Turn off the main 400V AC three-phase breaker and place your personal safety padlock and lockout tag.
2. **Hydraulic & Pneumatic Depressurization:** Open relief valve `V-102` until the pressure gauge reads `0 bar`.
3. **Thermal Check:** Wait 20 minutes if the housing temperature exceeds `65 °C`. Always wear cut-resistant gloves and safety glasses.

---

## SECTION 2: COMPONENT SPECIFICATIONS AND REPLACEMENT PROCEDURES

### 2.1 COMPONENT 1 (`comp1`): Main Electromechanical Drive Unit
**Page 12 · Primary Power and Spindle Drive**
* **Function:** Delivers high-speed rotational torque with axial stability.
* **Typical Sensor Degradation Symptoms:**
  * Sustained high **voltage (`volt > 180 V`)** combined with unstable **rotation speed (`rotate`)**.
  * Frequent **`error1`** alarms (Electrical overload in drive inverter).
* **Required Spare Part:** Main drive cartridge and brush kit `REF-C1-DRIVE-840D`.
* **Standard Repair Duration:** `4.0 hours` (1 technician).
* **Standard Preventive Cost:** `700 EUR` · **Unplanned Breakdown Cost:** `5,200 EUR`.
* **Step-by-Step Replacement Procedure (Page 14):**
  1. Lock the vertical axis in the middle position using safety block `CM-04`.
  2. Disconnect the 6-pin Harting power plug and the stator cooling hose.
  3. Loosen the 8 front flange M12 bolts in a cross pattern.
  4. Extract the damaged `comp1` cartridge using the hydraulic puller and clean the housing with residue-free solvent.
  5. Install the new `comp1` unit applying a **tightening torque of 85 Nm** with a calibrated torque wrench, and verify radial runout (`< 0.004 mm`).

---

### 2.2 COMPONENT 2 (`comp2`): High-Pressure Hydraulic Valve Assembly
**Page 27 · Clamping and Hydraulic Pressure Circuit**
* **Function:** Maintains a constant nominal pressure of `100 bar` in the clamping circuit.
* **Typical Sensor Degradation Symptoms:**
  * Sharp increase or erratic spikes in **pressure (`pressure > 115 bar`)** caused by valve clogging or pump cavitation.
  * Triggering of **`error2`** (Secondary pressure loop deviation) and **`error3`** (Hydraulic return filter clogging).
* **Required Spare Part:** Proportional hydraulic valve `4WREE-10` + 5-micron filter kit `REF-C2-HYD`.
* **Standard Repair Duration:** `3.0 hours`.
* **Standard Preventive Cost:** `500 EUR` · **Unplanned Breakdown Cost:** `4,400 EUR`.
* **Step-by-Step Replacement Procedure (Page 29):**
  1. Fully depressurize the nitrogen accumulator by opening purge valve `V-102` to `0 bar`.
  2. Place an oil drip tray under the manifold block and remove the 4 M8 Allen bolts holding the valve.
  3. Replace the Viton O-rings (`NBR-90`) lubricated with clean **ISO VG 46** hydraulic oil.
  4. Mount the new `comp2` valve applying a **tightening torque of 24 Nm** and replace the high-pressure filter element.
  5. Bleed trapped air by running 10 manual clamping cycles and calibrate nominal pressure to `100.0 ± 1.5 bar`.

---

### 2.3 COMPONENT 3 (`comp3`): Feed Axis Servomotor and Ball Screw Coupling
**Page 41 · Axis Feed Kinematics and Positioning**
* **Function:** Positions the main carriage with micrometric accuracy during heavy duty cycles.
* **Typical Sensor Degradation Symptoms:**
  * Significant drop in **effective rotation speed (`rotate < 400 RPM`)** caused by mechanical backlash or coupling wear.
  * Triggering of **`error4`** (Axis contour following error on optical encoder).
* **Required Spare Part:** Preloaded ball nut and flexible servo coupling assembly `REF-C3-SERVO-Z`.
* **Standard Repair Duration:** `5.0 hours`.
* **Standard Preventive Cost:** `800 EUR` · **Unplanned Breakdown Cost:** `5,800 EUR`.
* **Step-by-Step Replacement Procedure (Page 43):**
  1. Secure the carriage with a certified lifting sling (minimum capacity 1,500 kg) before releasing the motor coupling.
  2. Remove the bellows coupling (`R+W BK5`) and inspect the keyway and optical encoder shaft.
  3. Install the new `comp3` support and coupling assembly applying a **tightening torque of 42 Nm** on the radial clamping bolts.
  4. Lubricate the ball screw with synthetic lithium grease **Kluber Isoflex Topas NCA 52**.
  5. Run CNC reference routine `G74` to reset machine zero and verify backlash compensation.

---

### 2.4 COMPONENT 4 (`comp4`): High-Speed Angular Contact Bearings
**Page 58 · Main Shaft Mechanical Support**
* **Function:** Supports radial and axial loads without generating eccentricity or excessive heat.
* **Typical Sensor Degradation Symptoms:**
  * Exponential rise in **vibration (`vibration > 48 mm/s`)** and high 24-hour vibration standard deviation due to bearing raceway fatigue.
  * Triggering of **`error5`** (Piezoelectric accelerometer vibration threshold exceeded).
* **Required Spare Part:** Matched ceramic bearing set **SKF Super-Precision `7014 CD/HCP4A`** (`REF-C4-SKF`).
* **Standard Repair Duration:** `4.5 hours`.
* **Standard Preventive Cost:** `600 EUR` · **Unplanned Breakdown Cost:** `4,800 EUR`.
* **Step-by-Step Replacement Procedure (Page 60):**
  1. Remove the front labyrinth cover and extract the worn `comp4` bearings using an induction puller (never hit with a hammer).
  2. Inspect the shaft journal to ensure there is no fretting corrosion or scoring.
  3. Heat the new SKF bearings to `85 °C` on an induction heater and mount them in back-to-back (DB) arrangement matching the V-marks.
  4. Tighten precision locknut `KMT 14` to a **tightening torque of 65 Nm** and secure the bronze locking pins.
  5. Execute the mandatory 45-minute grease **run-in cycle** stepping from 1,000 to 8,000 RPM while monitoring bearing temperature.

---

## SECTION 3: QUICK ERROR CODE DIAGNOSTIC TABLE
**Page 72 · Quick Shop-Floor Troubleshooting Guide**

| Error Code | Technical Description | Altered Sensor | Component at Risk | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| **`error1`** | Drive inverter electrical overload | High `volt` (`>180 V`) | **`comp1`** (Main Drive) | Check phase current and replace `comp1` cartridge (Page 14). |
| **`error2`** | Secondary hydraulic pressure instability | High `pressure` (`>115 bar`) | **`comp2`** (Hydraulic Valve) | Inspect proportional valve and accumulator (Page 29). |
| **`error3`** | High differential pressure in hydraulic filter | Fluctuating `pressure` | **`comp2`** (Hydraulic Valve) | Replace 5-micron filter and Viton O-rings (Page 29). |
| **`error4`** | Axis positioning following error | Low `rotate` (`<400 RPM`) | **`comp3`** (Servo & Coupling) | Check coupling backlash and lubricate ball screw (Page 43). |
| **`error5`** | Critical shaft vibration alarm | High `vibration` (`>48 mm/s`) | **`comp4`** (SKF Bearings) | Stop machine and replace SKF ceramic bearings (Page 60). |