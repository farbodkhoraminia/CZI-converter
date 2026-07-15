# CZI Converter

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue.svg)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/your_username/CZI_Converter/CI)

## 🌟 **Transforming High-Quality CZI Images into TIFF with Ease**

### **Unlock the Full Potential of Your ZEISS CZI Images**

**Carl Zeiss Image (CZI)** files are renowned for their exceptional quality and versatility, making them a top choice for researchers and professionals in various scientific fields. However, despite their superior imaging capabilities, CZI files often face compatibility challenges with many popular image analysis platforms. This is where **CZI Converter** steps in to bridge the gap, offering a seamless solution to convert your high-resolution CZI images into the universally compatible TIFF format.

---

## 📈 **Why CZI Images from ZEISS Stand Out**

- **Unmatched Image Quality:** CZI files capture intricate details with high resolution, enabling precise analysis and visualization.
- **Multi-Dimensional Data:** Support for multiple channels, time points, and Z-stacks, allowing comprehensive imaging studies.
- **Metadata-Rich:** Embeds extensive metadata, facilitating better data management and reproducibility in research.

While these features make CZI files indispensable for detailed imaging tasks, they also introduce compatibility hurdles.

---

## 🔄 **Why Convert CZI to TIFF?**

- **Universal Compatibility:** TIFF is a widely supported format across various image analysis tools, ensuring your data is accessible and usable without proprietary constraints.
- **Ease of Sharing:** TIFF files are easier to share and collaborate on, eliminating the need for specialized software to view or analyze images.
- **Integration with Analysis Pipelines:** Simplifies the integration of your imaging data into automated analysis workflows and platforms.

---

## 🛠️ **The Conversion Challenge**

Converting large CZI files (>2GB) to TIFF is **notoriously challenging** due to:

- **High Resource Consumption:** Large file sizes demand significant memory and processing power, often leading to system slowdowns or crashes.
- **Time-Intensive Processes:** Manual conversion can be tedious and time-consuming, especially when dealing with multiple large files.
- **Complexity in Handling Metadata:** Preserving essential metadata during conversion requires meticulous handling to maintain data integrity.

---

## 🚀 **Introducing CZI Converter: Your Automated Conversion Pipeline**

**CZI Converter** is designed to **simplify and accelerate** the conversion of CZI files to TIFF, addressing the challenges head-on:

- **Automated Workflow:** Monitors designated input folders and automatically processes new CZI files without manual intervention.
- **Optimized Performance:** Uses multi-threading to handle large files efficiently, significantly reducing conversion time.
- **Memory-Friendly:** Engineered to manage resources effectively, to operate smoothly even with large image sizes.
- **User-Friendly Configuration:** Easy-to-edit configuration files allow customization to fit your specific environment and requirements.
- **Comprehensive Logging:** Detailed logs keep you informed about the conversion status, errors, and progress, aiding in troubleshooting and optimization.

With **CZI Converter**, you can focus on your research and analysis, leaving the heavy lifting of file conversion to a reliable and efficient tool.

---
# 🚀 Getting Started

## 📦 Installation Guide

Follow these steps to install and set up **CZI Converter**:

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/farbodkhoraminia/CZI-Converter.git
cd CZI-converter
```

### 2️⃣ Set Up a Virtual Environment (Optional but Recommended)
- **On Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3️⃣ Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirement.txt
```

> On Ubuntu, the converter now tries the common PMA installation locations automatically and also checks your PATH. A manual override in `config.yaml` is still supported.

### 4️⃣ Configure the Application
Open the `config.yaml` file in your text editor and set the paths for your platform.

**Example:**
```yaml
ASAP_BIN_PATH:
  windows: "C:/Program Files/ASAP 2.2/bin"
  linux: "/opt/asap/bin"
  ubuntu: "/opt/asap/bin"

PMA_EXECUTABLE_PATH:
  windows: "C:/Pathomation/PMA.start_converttif/Pathomation/Pathomation/pma.start.win/PMA.start.exe"
  linux: "/opt/pathomation/PMA.start"
  ubuntu: "/opt/pathomation/PMA.start"

INPUT_FOLDER: "data/input"
OUTPUT_FOLDER: "data/output"
```

Relative paths are resolved from the project root, so the default `data/input` and `data/output` folders will work on both Windows and Ubuntu.

#### Windows example
```yaml
ASAP_BIN_PATH:
  windows: "C:/Program Files/ASAP 2.2/bin"
PMA_EXECUTABLE_PATH:
  windows: "C:/Pathomation/PMA.start_converttif/Pathomation/Pathomation/pma.start.win/PMA.start.exe"
```

#### Ubuntu example
```yaml
ASAP_BIN_PATH:
  ubuntu: "/opt/asap/bin"
PMA_EXECUTABLE_PATH:
  ubuntu: "/opt/pathomation/PMA.start"
WORKERS: 16
```

#### Ubuntu performance tips
- Use the machine's available CPU count automatically by leaving `WORKERS` unset; the converter will select a sensible value.
- If your system has many cores, a value in the range `8-32` is often a good starting point.
- Ensure the PMA executable is either installed under `/opt/pathomation/PMA.start`, available in your PATH, or explicitly set in `config.yaml`.
- If PMA is unavailable, the converter now falls back to a local CZI reader using `czifile` and `tifffile`, which works well on Ubuntu for basic conversion.

### 5️⃣ Run the Converter
```bash
python main.py
```

You can also override the input folder from the terminal for a single run:
```bash
python main.py /path/to/your/input-folder
# or
python main.py --input-folder /path/to/your/input-folder
```

📂 **Logs:** Conversion logs are stored in the `logs` directory. Check the relevant `.log` file for progress updates or troubleshooting errors.


# ❓ FAQ & Troubleshooting

### ❓ What should I do if the converter crashes on large files?
✅ **Solution:** Reduce the number of threads in `config.yaml` by lowering `WORKERS`, or allocate more memory to your system.

### ❓ How do I fix missing dependencies?
✅ **Solution:** Reinstall all required dependencies:
```bash
pip install -r requirement.txt
```

### ❓ Why is the conversion process slow?
✅ **Solution:** Optimize your system resources:
- Check your CPU and disk I/O usage.
- Adjust the thread count in `config.yaml` using `WORKERS`.
- On Ubuntu, leave `WORKERS` unset to let the converter auto-select a value based on the machine's CPU count.

### ❓ How can I modify advanced settings?
✅ **Solution:** Customize the `config.yaml` file:
- Adjust multi-threading levels for better performance.
- Change the polling interval with `CHECK_INTERVAL_SECONDS`.
- Tune stall detection with `STALL_TIMEOUT_SECONDS`.

### ❓ Where are my converted files stored?
✅ **Solution:** Converted files are saved in the directory specified by `OUTPUT_FOLDER` in `config.yaml`.
