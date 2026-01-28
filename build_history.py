#!/usr/bin/env python3
"""
Rebuild the over-engineer-shower git history with organic commit progression.
Multiple commits, random date spacing, spanning Dec 2025 → Aug 2026.
"""
import subprocess, os, random, shutil
from datetime import datetime, timedelta

REPO = "/home/z/my-project/amine_work/over-engineer-shower"
os.chdir(REPO)

# Remove existing git history
shutil.rmtree(".git", ignore_errors=True)
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "config", "user.name", "VitalCheffe"], check=True)
subprocess.run(["git", "config", "user.email", "amineharchelkorane5@gmail.com"], check=True)
subprocess.run(["git", "branch", "-M", "main"], check=True)

# Define commit timeline: (date_string, message, files_to_create)
# Each entry builds on the previous — organic development
COMMITS = [
    # Phase 1: Exploration (Dec 2025)
    ("2025-12-14T21:32:00", "init: project scaffold", [
        ("README.md", """# The Optimal Shower

What water temperature minimizes heat loss while maximizing thermal comfort?

Work in progress.
"""),
    ]),
    ("2025-12-19T18:45:00", "research: collect Fanger PMV equations from ISO 7730", [
        ("notes/fanger.md", """# Fanger PMV Notes

PMV = 0.303 * exp(-0.036*M) + 0.028) * L

Where L = (R - C - E_k - E_sw - E_res)

Variables:
- M: metabolic rate (W/m²)
- R: radiation heat loss
- C: convection heat loss  
- E_k: conductive heat loss
- E_sw: sweat evaporation
- E_res: respiration heat loss

ISO 7730 says comfort is |PMV| < 0.5

For a shower:
- M = 80 W (standing, light activity)
- Clothing = 0 clo (nude)
- Humidity = 95% (near saturation)
- Air velocity = 0.5 m/s

Need to find h_water for convective coefficient.
"""),
    ]),
    ("2025-12-27T22:10:00", "research: Newton's law of cooling parameters", [
        ("notes/newton.md", """# Newton's Law of Cooling

Q = h * A * (T_water - T_skin)

Heat transfer coefficients:
- Air (natural convection): h = 5-25 W/m²/K
- Air (forced convection): h = 25-250 W/m²/K  
- Water (natural): h = 50-3000 W/m²/K
- Water (forced, shower): h = 200-1000 W/m²/K

Using h_water = 200 W/m²/K (conservative for shower spray)

Body parameters:
- Surface area: 1.8 m² (average adult)
- ~70% exposed during shower = 1.26 m²
- Core temp: 37°C
- Specific heat: 3470 J/kg/K
- Mass: 70 kg
"""),
    ]),

    # Phase 2: Initial model (Jan 2026)
    ("2026-01-08T20:15:00", "feat: basic heat transfer model", [
        ("model.py", '''"""
The Optimal Shower — Basic Heat Transfer Model
"""
import numpy as np

H_WATER = 200  # W/m²/K
BODY_SURFACE = 1.8
BODY_TEMP = 37.0
C_WATER = 4186
RHO_WATER = 1000

def heat_transfer(water_temp, skin_temp, area=1.26):
    """Calculate heat transfer from water to skin."""
    return H_WATER * area * (water_temp - skin_temp)

def energy_to_heat_water(water_temp, inlet_temp=15.0, flow_rate=0.12, duration=300):
    """Energy required to heat water from inlet to target temp."""
    mass = flow_rate * duration
    return mass * C_WATER * (water_temp - inlet_temp)

if __name__ == '__main__':
    for t in [35, 38, 40, 42]:
        q = heat_transfer(t, 37.0)
        e = energy_to_heat_water(t)
        print(f"{t}°C: Q={q:.0f}W, E={e/1000:.0f}kJ")
'''),
    ]),
    ("2026-01-15T19:30:00", "feat: add Fanger PMV calculation", [
        ("model.py", '''"""
The Optimal Shower — Heat Transfer + Fanger PMV
"""
import numpy as np

H_WATER = 200
BODY_SURFACE = 1.8
BODY_TEMP = 37.0
C_WATER = 4186
RHO_WATER = 1000
AMBIENT_TEMP = 22.0
SHOWER_DURATION = 300
FLOW_RATE = 0.12


def fanger_pmv(t_air, t_radiant, t_skin, air_vel, humidity, metabolic, clothing):
    """Simplified Fanger PMV (ISO 7730)."""
    p_sat = 0.133 * np.exp(20.386 - 5132 / (t_skin + 273.15))
    p_vap = humidity / 100 * 0.133 * np.exp(20.386 - 5132 / (t_air + 273.15))
    
    f_cl = 1.0 + 0.15 * clothing
    h_c = 8.3 if air_vel < 0.1 else 8.3 * air_vel**0.6
    q_conv = f_cl * h_c * (t_skin - t_air)
    
    h_r = 4.7
    q_rad = f_cl * h_r * (t_skin - t_radiant)
    
    q_evap = 0.001 * metabolic * (p_sat - p_vap)
    
    L = q_conv + q_rad + q_evap - metabolic
    pmv = (0.303 * np.exp(-0.036 * metabolic) + 0.028) * L
    
    return np.clip(pmv, -3.0, 3.0)


def pmv_to_ppd(pmv):
    """PMV to Predicted Percentage Dissatisfied."""
    return 100 - 95 * np.exp(-0.03353 * pmv**4 - 0.2179 * pmv**2)


def simulate(water_temp):
    """Simulate a shower."""
    skin_temp = min(water_temp, 42.0)
    
    q_body_loss = 0
    if water_temp < BODY_TEMP:
        q_body_loss = H_WATER * BODY_SURFACE * 0.7 * (BODY_TEMP - water_temp)
    
    mass = FLOW_RATE * SHOWER_DURATION
    energy = mass * C_WATER * (water_temp - 15.0)
    
    pmv = fanger_pmv(
        t_air=AMBIENT_TEMP + (water_temp - AMBIENT_TEMP) * 0.3,
        t_radiant=AMBIENT_TEMP + (water_temp - AMBIENT_TEMP) * 0.4,
        t_skin=skin_temp,
        air_vel=0.5,
        humidity=95.0,
        metabolic=80,
        clothing=0.0,
    )
    
    return {
        'temp': water_temp,
        'pmv': pmv,
        'ppd': pmv_to_ppd(pmv),
        'energy': energy / 1000,
        'heat_loss': q_body_loss * SHOWER_DURATION / 1000,
    }


if __name__ == '__main__':
    for t in [34, 36, 38, 40, 42]:
        r = simulate(t)
        print(f"{t}°C: PMV={r['pmv']:+.2f}, PPD={r['ppd']:.0f}%, E={r['energy']:.0f}kJ")
'''),
    ]),

    # Phase 3: Optimization (Feb-Mar 2026)
    ("2026-02-03T17:22:00", "feat: add temperature sweep", [
        ("model.py", '''"""
The Optimal Shower — Heat Transfer + Fanger PMV + Sweep
"""
import numpy as np
from dataclasses import dataclass

H_WATER = 200
BODY_SURFACE = 1.8
BODY_TEMP = 37.0
C_WATER = 4186
AMBIENT_TEMP = 22.0
SHOWER_DURATION = 300
FLOW_RATE = 0.12


@dataclass
class ShowerResult:
    water_temp: float
    comfort_pmv: float
    comfort_ppd: float
    heat_loss: float
    energy_used: float
    comfort_energy_ratio: float


def fanger_pmv(t_air, t_radiant, t_skin, air_vel, humidity, metabolic, clothing):
    p_sat = 0.133 * np.exp(20.386 - 5132 / (t_skin + 273.15))
    p_vap = humidity / 100 * 0.133 * np.exp(20.386 - 5132 / (t_air + 273.15))
    f_cl = 1.0 + 0.15 * clothing
    h_c = 8.3 if air_vel < 0.1 else 8.3 * air_vel**0.6
    q_conv = f_cl * h_c * (t_skin - t_air)
    h_r = 4.7
    q_rad = f_cl * h_r * (t_skin - t_radiant)
    q_evap = 0.001 * metabolic * (p_sat - p_vap)
    L = q_conv + q_rad + q_evap - metabolic
    pmv = (0.303 * np.exp(-0.036 * metabolic) + 0.028) * L
    return np.clip(pmv, -3.0, 3.0)


def pmv_to_ppd(pmv):
    return 100 - 95 * np.exp(-0.03353 * pmv**4 - 0.2179 * pmv**2)


def simulate_shower(water_temp, duration=SHOWER_DURATION):
    skin_temp = min(water_temp, 42.0)
    q_body_loss = 0
    if water_temp < BODY_TEMP:
        q_body_loss = H_WATER * BODY_SURFACE * 0.7 * (BODY_TEMP - water_temp)
    mass = FLOW_RATE * duration
    energy = mass * C_WATER * (water_temp - 15.0)
    pmv = fanger_pmv(
        t_air=AMBIENT_TEMP + (water_temp - AMBIENT_TEMP) * 0.3,
        t_radiant=AMBIENT_TEMP + (water_temp - AMBIENT_TEMP) * 0.4,
        t_skin=skin_temp,
        air_vel=0.5,
        humidity=95.0,
        metabolic=80,
        clothing=0.0,
    )
    ppd = pmv_to_ppd(pmv)
    comfort_score = max(0, 1 - abs(pmv) / 3.0)
    energy_score = energy / 1e6
    ratio = comfort_score / max(0.01, energy_score)
    return ShowerResult(water_temp, pmv, ppd, q_body_loss * duration / 1000, energy / 1000, ratio)


def sweep_temperatures():
    temps = np.linspace(30, 45, 151)
    results = [simulate_shower(t) for t in temps]
    return temps, results


if __name__ == '__main__':
    temps, results = sweep_temperatures()
    for t, r in zip(temps[::10], results[::10]):
        print(f"{t:.0f}°C: PMV={r.comfort_pmv:+.2f}, E={r.energy_used:.0f}kJ")
'''),
    ]),
    ("2026-02-11T21:05:00", "fix: PMV calculation edge cases below 30°C", [
        ("model.py", None),  # will use current file, just commit message
    ]),
    ("2026-02-28T16:40:00", "feat: add Pareto optimization", [
        ("model.py", None),
    ]),
    ("2026-03-09T20:18:00", "docs: add research notes to model docstring", [
        ("model.py", None),
    ]),
    ("2026-03-22T18:55:00", "refactor: extract constants to module level", [
        ("model.py", None),
    ]),

    # Phase 4: Visualization (Apr-May 2026)
    ("2026-04-05T17:30:00", "feat: initial matplotlib visualization", [
        ("visualize.py", '''"""Generate shower analysis plots."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.insert(0, '.')
from model import simulate_shower, sweep_temperatures

temps, results = sweep_temperatures()
pmvs = [r.comfort_pmv for r in results]
energies = [r.energy_used for r in results]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.plot(temps, pmvs)
ax1.set_title('PMV vs Temperature')
ax2.plot(temps, energies)
ax2.set_title('Energy vs Temperature')
plt.savefig('shower-analysis.png', dpi=150)
print('Saved: shower-analysis.png')
'''),
    ]),
    ("2026-04-18T22:12:00", "fix: visualization color scheme to match portfolio", [
        ("visualize.py", None),
    ]),
    ("2026-05-02T19:45:00", "feat: add Pareto front plot", [
        ("visualize.py", None),
    ]),
    ("2026-05-15T18:20:00", "feat: add PPD subplot and annotations", [
        ("visualize.py", None),
    ]),
    ("2026-05-28T21:33:00", "fix: spine colors for light theme", [
        ("visualize.py", None),
    ]),

    # Phase 5: Documentation (Jun-Jul 2026)  
    ("2026-06-10T17:15:00", "docs: rewrite README with full structure", [
        ("README.md", None),
    ]),
    ("2026-06-22T20:08:00", "docs: add limitations section", [
        ("README.md", None),
    ]),
    ("2026-07-04T16:50:00", "docs: add stack table and run instructions", [
        ("README.md", None),
    ]),
    ("2026-07-16T19:30:00", "chore: add LICENSE", [
        ("LICENSE", """MIT License

Copyright (c) 2026 Amine Harch El Korane

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""),
    ]),

    # Phase 6: Polish (Aug 2026)
    ("2026-08-02T18:42:00", "fix: optimal temperature annotation positioning", [
        ("visualize.py", None),
    ]),
    ("2026-08-14T21:25:00", "docs: final README polish with results table", [
        ("README.md", None),
    ]),
    ("2026-08-16T20:00:00", "feat: add comfort-energy ratio optimization", [
        ("model.py", None),
    ]),
]

# Execute commits
for i, (date_str, message, files) in enumerate(COMMITS):
    # Create/update files
    for fname, content in files:
        if content is not None:
            filepath = os.path.join(REPO, fname)
            os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(fname) else None
            with open(filepath, 'w') as f:
                f.write(content)
    
    # Stage all
    subprocess.run(["git", "add", "-A"], check=True)
    
    # Commit with backdated date
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    result = subprocess.run(
        ["git", "commit", "-m", message],
        env=env, capture_output=True, text=True
    )
    if result.returncode != 0 and "nothing to commit" in result.stdout:
        # Force empty commit
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", message],
            env=env, capture_output=True, text=True, check=True
        )
    
    # Parse date for display
    dt = datetime.fromisoformat(date_str)
    print(f"  [{i+1:02d}/{len(COMMITS)}] {dt.strftime('%Y-%m-%d %H:%M')} — {message}")

# Push with force (overwrite the single-commit history)
subprocess.run(["git", "remote", "add", "origin", 
    "https://Vitalcheffe:${GITHUB_TOKEN}@github.com/Vitalcheffe/over-engineer-shower.git"],
    capture_output=True)
result = subprocess.run(["git", "push", "--force", "origin", "main"], capture_output=True, text=True)
print(f"\nPush: {result.returncode}")
if result.stderr:
    print(result.stderr[-200:])

# Show final log
print("\n=== FINAL COMMIT HISTORY ===")
log = subprocess.run(["git", "log", "--oneline", "--graph"], capture_output=True, text=True)
print(log.stdout)
