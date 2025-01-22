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
git clone https://github.com/your_username/CZI_Converter.git
cd CZI_Converter
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
pip install -r requirement.txt
```

### 4️⃣ Configure Input and Output Paths
Open the `config.json` file in your text editor and specify the input and output paths.

**Example:**
```json
{
    "input_folder": "path/to/input_folder",
    "output_folder": "path/to/output_folder"
}
```

### 5️⃣ Run the Converter
```bash
python czi_converter.py
```

📂 **Logs:** Conversion logs are stored in the `logs` directory. Check the relevant `.log` file for progress updates or troubleshooting errors.


# ❓ FAQ & Troubleshooting

### ❓ What should I do if the converter crashes on large files?
✅ **Solution:** Reduce the number of threads in `config.json` or allocate more memory to your system.

### ❓ How do I fix missing dependencies?
✅ **Solution:** Reinstall all required dependencies:
```bash
pip install -r requirements.txt
```

### ❓ Why is the conversion process slow?
✅ **Solution:** Optimize your system resources:
- Check your CPU and disk I/O usage.
- Adjust the thread count in `config.json`.

### ❓ How can I modify advanced settings?
✅ **Solution:** Customize the `config.json` file:
- Adjust multi-threading levels for better performance.
- Change logging verbosity for detailed debugging.
- Optimize memory settings to handle large files.

### ❓ Where are my converted files stored?
✅ **Solution:** Converted files are saved in the directory specified in the `output_folder` field of the `config.json` file.
