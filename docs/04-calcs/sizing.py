"""BinLevel sizing calculations, BNL-CAL-001 v0.3 (TRL 3, design for construction, DDR-003).

Run from the repo root:  python docs/04-calcs/sizing.py
Prints every number quoted in docs/04-calcs/01-sizing.md. Each line carries a tag such as
[C3] that the note cites. Geometry comes from cad/src/model.py (PARAMS and derived), the
parts cost from bom/bom.csv and the budget from project.yaml. First-principles estimates
for a paper proof of concept; not a substitute for tests.
"""
import csv
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad" / "src"))
from model import PARAMS as P, derived, build_parts, build_components  # noqa: E402

D = derived(P)


def tag(t, text):
    print(f"[{t}] {text}")


# ------------------------------------------------------------------ assumptions
FILL_ALERT = 0.80          # default threshold (DDR-001, D6)
US_BLIND = 0.25            # m, ultrasonic blind zone of a sealed low-cost transducer (estimate)
US_MAX = 4.0               # m, conservative maximum range of a JSN-SR04T-class module (assumed)
US_HALF = 15.0             # deg, assumed effective half-angle of the ultrasonic beam
TOF_MAX = 0.40             # m, range used for the ToF sensor (short-distance mode, dirty targets)
TOF_FOV = 27.0             # deg, VL53L1X typical full field of view (ST product page)
F_US = 40e3                # Hz
T_CAL = 20.0               # degC, calibration temperature
T_RANGE = (-20.0, 70.0)    # degC, R6 range (upper limit raised from 60 degC, DDR-002)
DT_AIR = 5.0               # K, error between the on-board sensor and the air column (assumed)
TOF_ERR = 0.020            # m, ToF error including the window (assumed)
TIMER_RES = 1e-6           # s, echo timer resolution

# energy
V_CELL = 3.6
I_SLEEP = {                # uA
    "module in stop mode (RAK3172 datasheet 1.69 uA, rounded up)": 2.0,
    "accelerometer, wake-on-motion at 10 Hz (LIS2DH12 class, assumed)": 2.0,
    "temperature sensor in shutdown (assumed)": 0.5,
    "nanopower LDO quiescent, load switch and divider leakage (assumed)": 0.5,
    "buffer capacitor leakage (assumed)": 1.0,
}
RANGING = [                # (what, mA, s) per 15 min ranging cycle
    ("MCU awake", 3.0, 0.50),
    ("ultrasonic module, power-up and 5 pings at 60 ms", 10.0, 0.40),
    ("ToF sensor, two 50 ms ranges", 20.0, 0.10),
]
RANGINGS = 96              # per day
TEMP_READS = 288           # per day (every 5 min), 5 ms at 3 mA each
I_TX = 45.0                # mA at +14 dBm (assumed; datasheet gives 87 mA at +20 dBm only)
I_RX, T_RX_MIN = 6.0, 0.10 # mA, s minimum per receive window
I_PROC, T_PROC = 3.0, 0.5  # mA, s per uplink
ALERTS = 2                 # extra uplinks per day (threshold alert, tip or temperature)
CELLS = {"C (ER26500 class)": 8.5, "AA (ER14505 class)": 2.6}   # Ah nominal
USABLE = 0.60              # usable fraction for pulse loads, cold and end-of-life voltage
SELF_DIS = 0.01            # per year of nominal
V_OCV = 3.67               # V, fresh Li-SOCl2 open-circuit voltage
V_MOD_MAX = 3.6            # V, RAK3172 maximum supply (datasheet)

# radio
PAYLOAD = 11               # bytes application payload (revised from 12 so it fits US915 DR0)
OVERHEAD = 13              # MHDR 1, FHDR 7, FPort 1, MIC 4
US915_DR0_MAX = 11         # bytes, LoRaWAN Regional Parameters US902-928 DR0 (SF10/125)
DWELL = 0.400              # s, US915 dwell limit
TTN_S = 30.0               # s per day
DUTY = 0.01                # EU868 g1 sub-band
TX_DBM, G_NODE, L_NODE = 14.0, 0.0, 0.5
G_GW, L_GW, NF = 2.0, 2.0, 6.0
SNR_REQ = {7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}
H_GW, H_NODE, F_MHZ = 30.0, 1.3, 868.0
FADE = 10.0                # dB margin required
PEN = {"HDPE container, antenna under the lid": 10.0, "steel container, antenna inside": 30.0,
       "steel container, external lid antenna": 3.0}

# thermal
T_AMB_HOT = 40.0
G_SUN = 900.0              # W/m2
ALPHA = {"dark lid (0.90)": 0.90, "light lid (0.50)": 0.50}
H_OUT = 25.0               # W/m2K lid top, light wind
H_IN = 5.0                 # W/m2K lid underside
LID_RHO_CP = 950 * 1900.0  # J/m3K HDPE
UNIT_C = 400.0             # J/K unit heat capacity (about 0.4 kg at 1,000 J/kgK)
UNIT_G = 0.75              # W/K unit coupling to the lid (bracket contact plus air)
SUN_STEP = 800.0           # W/m2, cloud clears
G_CLOUD = 100.0            # W/m2, diffuse light under cloud before the sun breaks through (assumed)
RATE_GATE = 50.0           # degC, the 15 K rate-of-rise rule counts only above this (DDR-002)
RATE_K, ABS_ALERT = 15.0, 70.0

# mechanics
SHOCK_G = 20.0             # peak shock when the bin hits the lifter stop (assumed)
HDPE_SHEAR = 20e6          # Pa
WASHER_D = 18.0            # mm
M6_AS, M6_SY = 20.1, 210e6 # mm2 stress area; 210 MPa, a conservative yield for annealed A2 stainless
CELL_M = 0.050             # kg

# mass (g) of bought-in parts (assumed) and densities (g/cm3)
RHO = {"abs": 1.05, "steel": 7.9, "fr4": 1.85, "al": 2.68, "asa": 1.07, "pmma": 1.19}
BOUGHT = {"M6 x 20 bolts, nyloc nuts, plain and sealing washers (4 sets)": 36.0,
          "box fixings: M4 studs, aluminium standoffs, bonded seals, M4 screws, nylon standoffs": 22.0,
          "ultrasonic transducer and driver board, cable shortened": 30.0,
          "ToF breakout": 2.0, "LoRaWAN module on its breakout": 4.0, "breakouts, regulator, capacitor, wiring on the board": 12.0,
          "Li-SOCl2 C cell": 50.0, "cell holder, strap and fuse": 9.0, "antenna and lead": 3.0,
          "gasket, vent and cover screws": 6.0}


def airtime(n_bytes, sf, bw=125e3, cr=1, preamble=8):
    de = 1 if sf >= 11 else 0
    ts = (2 ** sf) / bw
    pl = n_bytes
    n = 8 + max(math.ceil((8 * pl - 4 * sf + 28 + 16) / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (preamble + 4.25) * ts + n * ts


def sound(t):
    return 331.3 * math.sqrt(1 + t / 273.15)


print("BinLevel sizing, BNL-CAL-001 v0.3\n")

# ------------------------------------------------------------------ A. measurement geometry
print("A. Measurement geometry (R1)")
h = D["face_to_floor"] / 1000
tag("A1", f"lid underside to inner floor {D['depth_lid']:.0f} mm; transducer face to floor {h * 1000:.0f} mm; "
          f"inner volume (box estimate) {D['inner_volume_l']:,.0f} L")
d80 = (1 - FILL_ALERT) * h
f_us_top = 1 - US_BLIND / h
f_tof_bot = 1 - TOF_MAX / h
tag("A2", f"80 % fill lies {d80 * 1000:.0f} mm below the face; ultrasonic blind zone {US_BLIND * 1000:.0f} mm "
          f"so ultrasonic reads fill up to {f_us_top * 100:.1f} %")
tag("A3", f"ToF to {TOF_MAX * 1000:.0f} mm covers fill from {f_tof_bot * 100:.1f} % to 100 %; overlap band "
          f"{f_tof_bot * 100:.1f} to {f_us_top * 100:.1f} % ({(TOF_MAX - US_BLIND) * 1000:.0f} mm) for cross-checking")
tag("A4", f"range needed 0 to {h:.2f} m; ultrasonic {US_BLIND} to {US_MAX} m (assumed), R1 target 0.03 to 1.5 m")
foot = 2 * h * math.tan(math.radians(US_HALF))
tof_foot = 2 * TOF_MAX * math.tan(math.radians(TOF_FOV / 2))
amax = math.degrees(math.atan(D["wall_clear"] / 1000 / h))
tag("A5", f"ultrasonic footprint at the floor {foot:.2f} m across at {US_HALF:.0f} deg half-angle; ToF footprint at "
          f"{TOF_MAX} m {tof_foot * 1000:.0f} mm across")
tag("A6", f"with the transducer {D['wall_clear']:.0f} mm from the nearest wall (center mount) the beam clears the walls "
          f"to the floor for half-angles up to {amax:.1f} deg")

# ------------------------------------------------------------------ B. accuracy
print("\nB. Instrument accuracy (R2)")
c20 = sound(T_CAL)
e_lo, e_hi = sound(T_RANGE[0]) / c20 - 1, sound(T_RANGE[1]) / c20 - 1
tag("B1", f"speed of sound {sound(T_RANGE[0]):.1f} to {sound(T_RANGE[1]):.1f} m/s over {T_RANGE[0]:.0f} to "
          f"{T_RANGE[1]:.0f} degC; uncompensated error {e_lo * 100:+.1f} % to {e_hi * 100:+.1f} % of distance")
e_t = (sound(T_CAL + DT_AIR) / c20 - 1)
e_temp = e_t * h
e_q = (c20 / F_US) / 2
e_timer = c20 * TIMER_RES / 2
e_us = math.sqrt(e_temp ** 2 + e_q ** 2 + e_timer ** 2)
allow = 0.10 * h
tag("B2", f"compensated with a {DT_AIR:.0f} K air-temperature error: {e_t * 100:.2f} % = {e_temp * 1000:.1f} mm at full depth; "
          f"half-wavelength echo jitter {e_q * 1000:.1f} mm; timer {e_timer * 1000:.2f} mm")
tag("B3", f"ultrasonic instrument error (RSS) {e_us * 1000:.1f} mm; ToF {TOF_ERR * 1000:.0f} mm; R2 allowance "
          f"+/-{allow * 1000:.0f} mm; instrument uses {e_us / allow * 100:.0f} % (ultrasonic), "
          f"{TOF_ERR / allow * 100:.0f} % (ToF); the rest is left for the waste surface, which is unknown")

# ------------------------------------------------------------------ C. energy
print("\nC. Energy and battery life (R4)")
i_sleep = sum(I_SLEEP.values())
q_sleep = i_sleep * 24 / 1000                                      # mAh/day
q_rng1 = sum(i * t for _, i, t in RANGING)                         # mAs
q_rng = q_rng1 * RANGINGS / 3600
q_temp = TEMP_READS * 3.0 * 0.005 / 3600
tag("C1", f"sleep {i_sleep:.1f} uA = {q_sleep:.3f} mAh/day; ranging {q_rng1:.2f} mAs per cycle x {RANGINGS} = "
          f"{q_rng:.3f} mAh/day; temperature every 5 min {q_temp:.4f} mAh/day")


def uplink_q(sf):
    ta = airtime(PAYLOAD + OVERHEAD, sf)
    t_rx = max(T_RX_MIN, 8 * (2 ** sf) / 125e3)
    return ta, (I_TX * ta + 2 * I_RX * t_rx + I_PROC * T_PROC) / 3600   # s, mAh


cases = {"SF9, hourly": (9, 24), "SF12, every 2 h": (12, 12)}
life = {}
for name, (sf, n) in cases.items():
    ta, q1 = uplink_q(sf)
    q_up = q1 * (n + ALERTS)
    for cell, cap in CELLS.items():
        q_sd = cap * 1000 * SELF_DIS / 365
        tot = q_sleep + q_rng + q_temp + q_up + q_sd
        yrs = cap * 1000 * USABLE / tot / 365
        life[(name, cell)] = (tot, yrs)
    tag("C2", f"{name}: {q1 * 1000:.2f} uAh per uplink, {n}+{ALERTS} uplinks = {q_up:.3f} mAh/day")
for (name, cell), (tot, yrs) in life.items():
    tag("C3", f"{name}, {cell}: {tot:.3f} mAh/day including self-discharge; life {yrs:.1f} years on {USABLE * 100:.0f} % usable")
worst_c = life[("SF12, every 2 h", "C (ER26500 class)")][1]
worst_aa = life[("SF12, every 2 h", "AA (ER14505 class)")][1]
avg_ua = life[("SF12, every 2 h", "C (ER26500 class)")][0] / 24 * 1000
tag("C4", f"worst case (SF12) average {avg_ua:.1f} uA including self-discharge; life {worst_c:.1f} years (C), {worst_aa:.1f} years (AA); "
          f"R4 needs 5 years minimum, 10 years design target")

# ------------------------------------------------------------------ D. supply and pulses
print("\nD. Supply voltage, pulses and heating (R6, R4)")
tag("D1", f"fresh cell open-circuit {V_OCV} V exceeds the module maximum {V_MOD_MAX} V by {(V_OCV - V_MOD_MAX) * 1000:.0f} mV: "
          f"a nanopower LDO (or similar) is needed on the carrier")
ta12 = airtime(PAYLOAD + OVERHEAD, 12)
c_full = I_TX / 1000 * ta12 / 0.5
tag("D2", f"a capacitor carrying a whole SF12 uplink ({I_TX:.0f} mA for {ta12:.2f} s) with 0.5 V droop needs "
          f"{c_full:.3f} F; the cell carries the pulse and a 1,000 uF low-leakage buffer covers voltage delay")
heat_mw = 20.0
tag("D3", f"a {heat_mw:.0f} mW window heater running all day would use {heat_mw / V_CELL * 24:.0f} mAh/day, "
          f"{heat_mw / V_CELL * 24 / life[('SF12, every 2 h', 'C (ER26500 class)')][0]:.0f} times the whole budget: not feasible")

# ------------------------------------------------------------------ E. airtime and payload
print("\nE. Airtime, payload and radio rules (R10, R3)")
for sf in range(7, 13):
    ta = airtime(PAYLOAD + OVERHEAD, sf)
    per_day_1h = ta * (24 + ALERTS)
    per_day_2h = ta * (12 + ALERTS)
    tag("E1", f"SF{sf}: {ta * 1000:.0f} ms per uplink; {per_day_1h:.1f} s/day hourly, {per_day_2h:.1f} s/day 2-hourly "
              f"(both with {ALERTS} alerts); EU868 1 % off-time {ta * (1 / DUTY - 1):.0f} s")
tag("E2", f"payload {PAYLOAD} bytes plus {OVERHEAD} overhead; US915 DR0 (SF10) allows {US915_DR0_MAX} bytes: "
          f"{'fits' if PAYLOAD <= US915_DR0_MAX else 'DOES NOT FIT'} (a 12-byte payload would not)")
ta10 = airtime(PAYLOAD + OVERHEAD, 10)
tag("E3", f"US915 SF10 airtime {ta10 * 1000:.0f} ms against the {DWELL * 1000:.0f} ms dwell limit")
ta11 = airtime(PAYLOAD + OVERHEAD, 11)
tag("E4", f"SF11 hourly would use {ta11 * (24 + ALERTS):.1f} s/day, SF12 hourly {ta12 * (24 + ALERTS):.1f} s/day, against TTN's {TTN_S:.0f} s: "
          f"so the routine interval stays 1 h up to SF11 and stretches to 2 h at SF12 only (DDR-002), "
          f"keeping SF12 at {ta12 * (12 + ALERTS):.1f} s/day")

# ------------------------------------------------------------------ F. link budget
print("\nF. Link budget (R10)")


def hata_urban(d_km):
    a = (1.1 * math.log10(F_MHZ) - 0.7) * H_NODE - (1.56 * math.log10(F_MHZ) - 0.8)
    return (69.55 + 26.16 * math.log10(F_MHZ) - 13.82 * math.log10(H_GW) - a
            + (44.9 - 6.55 * math.log10(H_GW)) * math.log10(d_km))


def hata_range(loss):
    a = (1.1 * math.log10(F_MHZ) - 0.7) * H_NODE - (1.56 * math.log10(F_MHZ) - 0.8)
    base = 69.55 + 26.16 * math.log10(F_MHZ) - 13.82 * math.log10(H_GW) - a
    return 10 ** ((loss - base) / (44.9 - 6.55 * math.log10(H_GW)))


for sf in (9, 12):
    sens = -174 + 10 * math.log10(125e3) + NF + SNR_REQ[sf]
    budget = TX_DBM + G_NODE - L_NODE + G_GW - L_GW - sens
    tag("F1", f"SF{sf}: sensitivity {sens:.1f} dBm; link budget {budget:.1f} dB; urban Hata loss at 1 km {hata_urban(1):.1f} dB")
    for pen_name, pen in PEN.items():
        m1 = budget - pen - hata_urban(1)
        rng = hata_range(budget - pen - FADE)
        tag("F2", f"SF{sf}, {pen_name} ({pen:.0f} dB): margin at 1 km {m1:.1f} dB; range with {FADE:.0f} dB fade margin {rng:.2f} km")

# ------------------------------------------------------------------ G. timing
print("\nG. Timing (R3, R9)")
wait = ta12 * (1 / DUTY - 1)
lat = 15 * 60 + wait + ta12
tag("G1", f"fill alert worst case: 15 min ranging interval + {wait:.0f} s EU868 off-time + {ta12:.1f} s airtime = {lat / 60:.1f} min (R3: 20 min)")
lat_t = 5 * 60 + wait + ta12
lat_t15 = 15 * 60 + wait + ta12
tag("G2", f"temperature alert worst case: {lat_t / 60:.1f} min with 5 min temperature reads, {lat_t15 / 60:.1f} min if read only "
          f"with the 15 min ranging (R9: 15 min)")

# ------------------------------------------------------------------ H. thermal
print("\nH. Temperature under the lid (R6, R9)")
for n, a in ALPHA.items():
    t_lid = T_AMB_HOT + a * G_SUN / (H_OUT + H_IN)
    tag("H1", f"{n}: lid at about {t_lid:.0f} degC in {G_SUN:.0f} W/m2 sun at {T_AMB_HOT:.0f} degC ambient")
tau_lid = LID_RHO_CP * P["lid_t"] / 1000 / (H_OUT + H_IN)
tau_unit = UNIT_C / UNIT_G
dT = ALPHA["dark lid (0.90)"] * SUN_STEP / (H_OUT + H_IN)
# two first-order stages: lid, then the unit
t_lid, t_unit, dt = 0.0, 0.0, 1.0
for _ in range(int(15 * 60 / dt)):
    t_lid += (dT - t_lid) / tau_lid * dt
    t_unit += (t_lid - t_unit) / tau_unit * dt
tag("H2", f"lid time constant {tau_lid / 60:.1f} min, unit {tau_unit / 60:.1f} min; when {SUN_STEP:.0f} W/m2 sun breaks "
          f"through, a dark lid rises {dT:.0f} K and the unit {t_unit:.1f} K within 15 min (R9 rate trigger 15 K)")



def unit_rise(step):
    """Unit temperature rise within 15 min after a sun step of `step` W/m2 on a dark lid."""
    target = ALPHA["dark lid (0.90)"] * step / (H_OUT + H_IN)
    tl, tu = 0.0, 0.0
    for _ in range(int(15 * 60 / dt)):
        tl += (target - tl) / tau_lid * dt
        tu += (tl - tu) / tau_unit * dt
    return tu


t_cloud = T_AMB_HOT + ALPHA["dark lid (0.90)"] * G_CLOUD / (H_OUT + H_IN)
tag("H3", f"gated rate rule (count the {RATE_K:.0f} K rise only above {RATE_GATE:.0f} degC): under cloud ({G_CLOUD:.0f} W/m2) the unit "
          f"starts at about {t_cloud:.0f} degC, below the gate, so the sun step does not trigger; the steady dark lid "
          f"(about {T_AMB_HOT + ALPHA['dark lid (0.90)'] * G_SUN / (H_OUT + H_IN):.0f} degC) stays below the {ABS_ALERT:.0f} degC absolute alert")
g_gate = (RATE_GATE - T_AMB_HOT) * (H_OUT + H_IN) / ALPHA["dark lid (0.90)"]
rise_gate = unit_rise(G_SUN - g_gate)
tag("H4", f"worst case above the gate: a unit already at {RATE_GATE:.0f} degC (sun {g_gate:.0f} W/m2) that then sees full "
          f"{G_SUN:.0f} W/m2 sun rises {rise_gate:.1f} K in 15 min, "
          f"{'below' if rise_gate < RATE_K else 'ABOVE'} the {RATE_K:.0f} K trigger")

parts, bplate = build_parts(P)
COMP = build_components(P)
cv = {k: c.shape.volume / 1000 for k, c in COMP.items()}            # cm3
# ------------------------------------------------------------------ I. mass and size
print("\nI. Mass and size (R16)")
m_enc = (cv["base"] + cv["cover"]) * RHO["abs"]
mat = P.get("plate_mat", "steel")
mat_name = {"al": "5052-class aluminium", "steel": "stainless"}[mat]
m_brk = cv["plate"] * RHO[mat]
m_pcb = cv["board"] * RHO["fr4"]
m_print = (cv["collar"] + cv["tof_holder"]) * RHO["asa"] + cv["window"] * RHO["pmma"]
m_total = m_enc + m_brk + m_pcb + m_print + sum(BOUGHT.values())
tag("I1", f"enclosure {m_enc:.0f} g; bracket plate ({P['plate_t']} mm {mat_name}, no tabs) {m_brk:.0f} g; board {m_pcb:.0f} g; "
          f"printed collar and ToF holder with window {m_print:.0f} g; bought-in parts {sum(BOUGHT.values()):.0f} g; "
          f"total {m_total:.0f} g (R16: 400 g)")
v_per_mm = cv["plate"] / P["plate_t"]                      # cm3 per mm of plate thickness
for t, m in ((1.5, "steel"), (2.0, "steel")):
    m_alt = v_per_mm * t * RHO[m]
    tag("I2", f"for comparison, a {t} mm stainless plate is {m_alt:.0f} g and the unit {m_total - m_brk + m_alt:.0f} g")
fp = D["footprint"]
tag("I3", f"below the lid {fp[0]:.0f} x {fp[1]:.0f} x {D['below_lid']:.1f} mm (R16: 160 x 90 x 100 mm)")

# ------------------------------------------------------------------ J. mechanics
print("\nJ. Shock and fixing (R7)")
m_unit_est = m_total / 1000
f_unit = m_unit_est * SHOCK_G * 9.81
pull = math.pi * WASHER_D * P["lid_t"] * HDPE_SHEAR / 1e6
tag("J1", f"{SHOCK_G:.0f} g shock on a {m_unit_est:.2f} kg unit: {f_unit:.0f} N; one washer pull-through in the "
          f"{P['lid_t']:.0f} mm HDPE lid about {pull:,.0f} N; one M6 bolt at {M6_SY / 1e6:.0f} MPa about {M6_AS * M6_SY / 1e6:,.0f} N")
tag("J2", f"cell ({CELL_M * 1000:.0f} g) at {SHOCK_G:.0f} g needs {CELL_M * SHOCK_G * 9.81:.0f} N of retention; spring clips alone "
          f"are not relied on; a strap or potting pad is specified")

m_hang = (m_total - m_brk - 36.0) / 1000                      # everything hanging on the four studs
f_hang = m_hang * SHOCK_G * 9.81
abs_shear, seal_od, stud_push = 30e6, 9.0, 900.0
pull_abs = math.pi * seal_od * P["enc_wall"] * abs_shear / 1e6
tag("J3", f"the box and its contents ({m_hang * 1000:.0f} g) hang on four M4 studs: {f_hang:.0f} N at {SHOCK_G:.0f} g, "
          f"{f_hang / 4:.0f} N per stud; base floor pull-through under a {seal_od:.0f} mm sealing washer about {pull_abs:,.0f} N per stud "
          f"(ABS shear {abs_shear / 1e6:.0f} MPa, assumed); stud push-out in 2 mm aluminium about {stud_push:.0f} N (assumed, maker's data to confirm)")

# ------------------------------------------------------------------ K. cost
print("\nK. Cost (R14)")
budget = None
for line in (ROOT / "project.yaml").read_text().splitlines():
    if line.startswith("budget_usd:"):
        budget = float(line.split(":")[1].split("#")[0])
total = 0.0
with open(ROOT / "bom" / "bom.csv", newline="") as f:
    rows = list(csv.DictReader(f))
for r in rows:
    total += float(r["qty"]) * float(r["unit_cost_usd"])
tag("K1", f"{len(rows)} BOM lines, all priced; parts total ${total:.2f} against budget_usd ${budget:.0f}: "
          f"{'within' if total <= budget else 'OVER'} by ${abs(budget - total):.2f}")
ext_ant = 8.0
tag("K2", f"with the external lid antenna for steel containers (about ${ext_ant:.0f}, open item O1) the total is "
          f"${total + ext_ant:.2f}, {'over' if total + ext_ant > budget else 'within'} budget")
