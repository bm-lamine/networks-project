# GSM Cellular Network Planning: Theory & Implementation

## THEORETICAL CONCEPTS

### 1. Hexagonal Cell Tessellation

**Why Hexagons?**

- Circles leave gaps and overlap inefficiently
- Hexagons tile perfectly without gaps or overlap
- Hexagons approximate circles better than squares
- Provides uniform coverage with minimal overlap

**Mathematical Properties:**

- Cell area: `A = (3√3/2) × R²` where R is the radius
- 6 sides means 6 nearest neighbors
- Regular hexagons have all sides equal

### 2. Frequency Reuse Concept

**The Problem:**

- Limited radio spectrum (e.g., 124 channels in GSM)
- Need to serve many cells
- Same frequency creates interference

**The Solution:**

- Divide channels into N groups (cluster size)
- Assign each group to different cells
- Reuse same frequencies in cells separated by distance D

**Key Formula:**

```
Channels per cell = Total Channels / N
```

For GSM with 124 channels:

- N=3: 41 channels/cell
- N=7: 17 channels/cell
- N=12: 10 channels/cell

### 3. Path Loss Model (Log-Distance)

**Formula:**

```
PL(d) = PL(d₀) + 10·n·log₁₀(d/d₀)
```

**Parameters:**

- **d₀**: Reference distance (typically 1 km)
- **n**: Path loss exponent
  - n=3.0: Rural (open area, few obstacles)
  - n=3.5: Suburban (some buildings, trees)
  - n=4.0: Urban (dense buildings, high attenuation)

**Physical Meaning:**

- Larger n → faster signal decay → smaller cells needed
- Urban environments need more base stations
- Rural areas can use larger cells

### 4. Cell Radius Calculation

**Link Budget Approach:**

```
P_TX + G_ant - PL(R) ≥ P_sens
```

Solving for R:

```
R = d₀ × 10^(PL_max/(10·n))
where PL_max = P_TX + G_ant - P_sens
```

**Two-Way Check:**

- Downlink: BTS → Mobile (BTS transmits at 43 dBm)
- Uplink: Mobile → BTS (Mobile transmits at 23 dBm)
- Final R = minimum of both (limited by weakest link)

**Example Calculation:**

```
Downlink: P_BTS=43 dBm, P_sens=-100 dBm, G_ant=2 dB
PL_max = 43 + 2 - (-100) = 145 dB
R = 1 × 10^(145/(10×3.5)) = 8.456 km
```

### 5. Reuse Distance

**Formula:**

```
D = R × √(3N)
```

**Why This Formula?**

- Derived from hexagonal geometry
- D is the minimum distance between co-channel cells
- For N=7: D = R × √21 ≈ 4.58R

**Examples:**

| N   | √(3N) | D/R Ratio |
| --- | ----- | --------- |
| 3   | 3.00  | 3.00      |
| 4   | 3.46  | 3.46      |
| 7   | 4.58  | 4.58      |
| 9   | 5.20  | 5.20      |
| 12  | 6.00  | 6.00      |

### 6. Signal-to-Interference Ratio (S/I)

**The Interference Problem:**

- First ring of interferers has 6 co-channel cells
- Each interferer contributes interference power

**Formula:**

```
S/I = (D/R)^n / 6
S/I_dB = 10·log₁₀((D/R)^n / 6)
```

**Substituting D = R√(3N):**

```
S/I_dB = 10·log₁₀((√(3N))^n / 6)
S/I_dB = 10·n·log₁₀(√(3N)) - 10·log₁₀(6)
S/I_dB = 5n·log₁₀(3N) - 7.78
```

**GSM Requirement:**

- Minimum S/I = 17-18 dB for acceptable voice quality
- Below this: dropped calls, poor audio quality

**Example for N=7, n=3.5:**

```
S/I = (√21)^3.5 / 6
S/I = 116.7 / 6 = 19.45
S/I_dB = 10·log₁₀(19.45) = 12.89 dB + 7.00 dB = 19.89 dB ✓
```

### 7. Capacity Analysis

**Subscribers per Cell:**

```
Subscribers = Density × Cell_Area
Cell_Area = (3√3/2) × R²
```

**Active Users:**

```
Active = Subscribers × Activity_Rate
```

Typical activity rate = 10% (10% of users calling simultaneously)

**Capacity Constraint:**

```
Active Users ≤ Channels per Cell
```

**Example:**

- R = 8.456 km
- Area = 185.4 km²
- Density = 20 subscribers/km²
- Subscribers = 185.4 × 20 = 3708
- Active (10%) = 371 users
- Channels (N=7) = 124/7 = 17 channels
- **Result: OVERLOAD!** Need smaller cells or larger N

### 8. The Fundamental Trade-off

**Increasing N:**

- ✓ Better S/I (less interference)
- ✗ Fewer channels per cell (less capacity)

**Decreasing N:**

- ✓ More channels per cell (more capacity)
- ✗ Worse S/I (more interference)

**Why N=7 is Optimal for GSM:**

| N   | S/I (dB)  | Channels | Quality   | Capacity | Verdict            |
| --- | --------- | -------- | --------- | -------- | ------------------ |
| 3   | 8.92     | 41       | Poor      | Good     | ✗ Bad Quality      |
| 4   | 11.10     | 31       | Poor      | OK       | ✗ Below 17 dB      |
| 7   | **15.36** | **17**   | **Good**  | **OK**   | **✓ BEST** |
| 12  | 19.45    | 10       | Excellent | Very Low | ✗ Too Few Channels |

### 9. Environment Impact

**Urban (n=4.0):**

- High attenuation → Small cells (R≈6 km)
- Need many base stations (expensive)
- S/I easily satisfied (good separation)
- High capacity per area (many cells)

**Suburban (n=3.5):**

- Moderate attenuation → Medium cells (R≈8.5 km)
- Balanced cost and performance
- Standard GSM planning

**Rural (n=3.0):**

- Low attenuation → Large cells (R≈13 km)
- Fewer base stations (economical)
- S/I becomes critical (cells further apart needed)
- Lower capacity per area

---

## PRACTICAL CONCEPTS

### 1. The params.json File

**Purpose:**
Store all network parameters in one place for easy modification.

**Structure:**

```json
{
  "P_BTS_dBm": 43, // BTS transmit power
  "P_MS_dBm": 23, // Mobile transmit power
  "P_sens_dBm": -100, // Receiver sensitivity
  "N_f": 124, // Total available channels
  "f_port_MHz": 900, // Carrier frequency
  "N": 7, // Cluster size (reuse pattern)
  "SIR_min_dB": 17, // Minimum S/I requirement
  "Dst_ab": 20, // Subscriber density (per km²)
  "T_act": 0.1, // Activity rate (10%)
  "Pathloss_exp": 3.5, // Path loss exponent
  "d0_km": 1 // Reference distance
}
```

### 2. The Loading Problem

**Original Issue:**

```python
def load_params(filename='params.json'):
    with open(filename, 'r') as f:  # Opens from current directory
        params = json.load(f)
```

**Problem:**

- Python searches for files relative to the _current working directory_
- If you run the script from a different folder, it can't find params.json
- Example: Running from `/home/user/` looks for `/home/user/params.json`
- But the file is actually in `/home/user/project/params.json`

### 3. The Solution

**Fixed Code:**

```python
import os

def load_params(filename='params.json'):
    # Get the directory where THIS script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Build full path to params.json in same directory
    filepath = os.path.join(script_dir, filename)

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            params = json.load(f)
        print(f"✓ Loaded from {filepath}")
        return params
    else:
        # Fallback to current directory
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                params = json.load(f)
            return params
        else:
            print(f"⚠ File not found, using defaults")
            return get_default_params()
```

**Key Changes:**

1. `os.path.abspath(__file__)`: Gets full path to the script
2. `os.path.dirname()`: Gets the directory containing the script
3. `os.path.join()`: Safely combines directory + filename
4. `os.path.exists()`: Checks if file actually exists
5. Fallback mechanism for flexibility

### 4. How to Use

**File Structure:**

```
project/
├── back_end.py          ← Fixed version
├── front_end.py
├── params.json          ← Must be in same folder
└── test_params_loading.py
```

**Running:**

```bash
# Navigate to project directory
cd project/

# Run the test
python test_params_loading.py

# Run the main program
python front_end.py
```

### 5. Real-World Workflow

**Step 1: Edit Parameters**
Edit `params.json` to test different scenarios:

```json
{
  "N": 3, // Try N=3 (high capacity, poor quality)
  "Pathloss_exp": 4.0 // Try urban environment
}
```

**Step 2: Run Analysis**

```bash
python front_end.py
```

**Step 3: Interpret Results**

```
S/I obtained: 14.25 dB
S/I minimum:  17.00 dB
Status: ✗ INSUFFICIENT

Solution: Increase N to 7 or reduce cell radius
```

**Step 4: Adjust and Re-run**
Change `N` to 7, run again:

```
S/I obtained: 19.89 dB ✓
Channels/cell: 17
Active users: 22.0
Status: ✓ OK
```

### 6. Common Scenarios

**Scenario A: Dense Urban Area**

```json
{
  "Dst_ab": 100, // High density
  "Pathloss_exp": 4.0, // Urban environment
  "N": 7
}
```

Result: Small cells (R≈6 km), many base stations needed

**Scenario B: Rural Area**

```json
{
  "Dst_ab": 5, // Low density
  "Pathloss_exp": 3.0, // Rural environment
  "N": 7
}
```

Result: Large cells (R≈13 km), fewer base stations

**Scenario C: Capacity Crisis**

```json
{
  "Dst_ab": 50, // Very high density
  "N": 12 // Large N
}
```

Result: Capacity overload! Need to reduce N or R

### 7. Validation Checklist

**For ANY configuration, verify:**

✓ **S/I Check:**

```
Is S/I_obtained ≥ 17 dB?
If NO → Increase N or reduce R
```

✓ **Capacity Check:**

```
Is Active_Users ≤ Channels_per_Cell?
If NO → Decrease N or reduce R
```

✓ **Coverage Check:**

```
Is R achievable with given transmit powers?
Check both uplink and downlink
```

### 8. Understanding the Visualizations

**Hexagonal Grid:**

- Each hexagon = one cell
- Triangle marker = Base Station (BTS)
- Different colors = Different frequency groups

**Frequency Assignment:**

- F0, F1, ..., F(N-1) labels show frequency group
- Same color = Same frequencies
- Never adjacent = Avoids co-channel interference

**Pattern Recognition:**

- N=3: Simple 3-color pattern
- N=7: Complex 7-color rosette pattern
- N=12: Very complex pattern (rarely used)

---

## MATHEMATICAL DERIVATIONS

### Derivation 1: Cell Area

Hexagon with radius R (center to vertex):

- Side length = R
- Height = 2R
- Width = R√3

Area formula:

```
A = 6 × (Area of equilateral triangle)
A = 6 × (√3/4 × R²)
A = (3√3/2) × R²
```

### Derivation 2: Reuse Distance

For hexagonal tessellation with cluster size N:

- Shift i cells horizontally
- Shift j cells at 60° angle
- N = i² + ij + j²

For N=7: i=2, j=1

```
D² = (iR√3)² + (jR√3)² + (iR√3)(jR√3)cos(60°)
D² = 3R²(i² + j² + ij)
D² = 3NR²
D = R√(3N)
```

### Derivation 3: S/I Formula

Signal power at distance R:

```
S = P₀ / R^n
```

Interference from 6 cells at distance D:

```
I = 6 × P₀ / D^n
```

Signal-to-Interference Ratio:

```
S/I = (P₀/R^n) / (6×P₀/D^n)
S/I = (D/R)^n / 6
```

In dB:

```
S/I_dB = 10log₁₀((D/R)^n) - 10log₁₀(6)
S/I_dB = n×10log₁₀(D/R) - 7.78
```

---

## TROUBLESHOOTING

### Problem: params.json Not Loading

**Symptom:** Program uses default values instead of your params.json

**Solutions:**

1. **Use the fixed back_end.py** (provided above)
2. **Verify file location:**

   ```bash
   ls -la  # Check params.json is in same folder
   ```

3. **Check file permissions:**

   ```bash
   chmod 644 params.json
   ```

4. **Verify JSON syntax:**

   ```bash
   python -m json.tool params.json
   ```

### Problem: S/I Not Satisfied

**Symptom:** S/I_obtained < 17 dB

**Solutions:**

1. **Increase N** (more separation between co-channel cells)
2. **Reduce R** (smaller cells)
3. **Increase transmit power** (limited by regulations)
4. **Use directional antennas** (not in this model)

### Problem: Capacity Overload

**Symptom:** Active_Users > Channels_per_Cell

**Solutions:**

1. **Decrease N** (more channels per cell)
2. **Reduce R** (fewer subscribers per cell)
3. **Deploy more cells** (split coverage area)
4. **Upgrade to 3G/4G** (more spectral efficiency)

---

## CONCLUSION

This project demonstrates the fundamental trade-offs in cellular network design:

1. **Coverage vs Capacity:** Large cells = good coverage but limited capacity
2. **Quality vs Capacity:** High S/I = good quality but fewer channels
3. **Cost vs Performance:** More base stations = better service but higher cost

The fixed `back_end.py` ensures reliable parameter loading, making experimentation easier and more reliable.
