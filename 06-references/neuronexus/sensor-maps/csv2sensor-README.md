# csv2sensor: Custom Sensor Definition Tool

`csv2sensor` is a command-line utility for converting custom sensor definition CSV files into Radiens-compatible Headstage (`.hstg`) and Probe (`.prb`) configuration files.

## Usage

```bash
csv2sensor -type <headstage|probe> [options] <csv-file>
```

### Options

* **`-type`** (Required): The type of file to generate.
  * `headstage`: Generates a `.hstg` mapping file.
  * `probe`: Generates a `.prb` geometry file.
* **`-out-dir`** (Optional): Directory to save the output files.
  * Default: Your local user devices directory. You can see this path by running `csv2sensor -h`.

### Arguments

* `<csv-file>`: Path to the input CSV file.

## Output Files

The tool automatically generates filenames compatible with the Radiens platform:

* **Headstage**: `hstg__usrdef_<filename>.hstg`
* **Probe**: `probe__usrdef_<filename>.prb`

For example, input `my_sensor.csv` becomes `hstg__usrdef_my_sensor.hstg`.

If the output file already exists, you will be prompted to confirm before overwriting.

## CSV Format Specification

The input file can use **Comma**, **Tab**, **Semicolon**, or **Pipe** delimiters. The tool automatically detects the delimiter and the header row. Define your columns using **case-insensitive** headers (e.g., "Site Num" is treated as `site_num`).

### 1. Creating a Headstage File (`-type headstage`)

Use this option to generate a `.hstg` file, which maps hardware channels (native indexes) to electrode sites.

**Supported Headers:**

| Header | Required? | Description |
| --- | --- | --- |
| `ntv_chan` | **Yes** | Native hardware channel index (0-indexed). |
| `site_num` | **Yes** | Electrode site number (1-indexed). |

**Example CSV:**

```csv
ntv_chan, site_num
0, 1
1, 2
2, 3
3, 4
4, 5
5, 6
6, 7
7, 8
8, 9
9, 10
10, 11
11, 12
12, 13
13, 14
14, 15
15, 16
```

---

### 2. Creating a Probe File (`-type probe`)

Use this option to generate a `.prb` file, which defines the physical geometry of the electrode sites.

#### Site Geometry Headers

Each row in the CSV defines one electrode site. The number of rows determines the number of sites.

| Header | Required? | Description |
| --- | --- | --- |
| `site_num` | **Yes** | Electrode site number (1-indexed). |
| `center_x` | No | X coordinate of site center in microns. (Default: Auto-grid) |
| `center_y` | No | Y coordinate of site center in microns. (Default: Auto-grid) |
| `center_z` | No | Z coordinate of site center in microns. (Default: 0) |
| `shape` | No | Site shape: `circle` or `rect`. (Default: `circle`) |
| `radius` | No | Radius for circular sites in microns. Also used as half-width/height for rectangular sites if `rect_width`/`rect_height` are not specified. (Default: 5.0) |
| `rect_width` | No | Full width for rectangular sites in microns. Only applies when `shape` is `rect`. (Default: `radius * 2`) |
| `rect_height` | No | Full height for rectangular sites in microns. Only applies when `shape` is `rect`. (Default: `radius * 2`) |

#### Wireframe Headers (Optional)

The wireframe columns define the **probe outline** for visualization. Unlike the site columns above, these are **not per-site**. Instead, they define a series of (x, y) vertices that draw the probe's physical shape.

* The wireframe can have a different number of rows than the site list.
* `wfx` and `wfy` must have the same number of entries.
* If omitted, no custom outline is drawn.

| Header | Description |
| --- | --- |
| `wfx` | Wireframe vertex X coordinate in microns. |
| `wfy` | Wireframe vertex Y coordinate in microns. |

**Example CSV (sites only):**

```csv
site_num, x, y, radius
1, 0, 0,  6
2, 0, 20, 6
3, 0, 40, 6
4, 0, 60, 6
```

**Example CSV (sites with wireframe outline):**

```csv
site_num, center_x, center_y, radius, wfx, wfy
1, 0, 0,  6, -10, -10
2, 0, 20, 6, 10, -10
3, 0, 40, 6, 10, 70
4, 0, 60, 6, -10, 70
```

## Examples

We have provided example CSV files in the release bundle (`example_headstage_64ch.csv` and `example_probe_32ch.csv`). You can run the following commands to test them:

```bash
# Generate a headstage file in the default directory using the provided example
csv2sensor -type headstage example_headstage_64ch.csv

# Generate a probe file in a specific folder using the provided example
csv2sensor -type probe -out-dir ./output/ example_probe_32ch.csv
```
