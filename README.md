# 🛡️ Oasis

> **A FOSS web application for Text Analysis and Image Privacy.**
> *Detect Plagiarism. Identify AI Writing. Scrub Image Metadata.*

---

## 🧩 About The Project

**Oasis** is a privacy-focused, open-source web tool designed to help students, writers, and developers ensure the authenticity of their content and the privacy of their media. 

Unlike many commercial tools, this project runs **entirely locally**. It relies on mathematical models and open-source libraries rather than paid, external APIs. This ensures that your data never leaves your machine.

### 🌟 Key Features
* **🚫 Plagiarism Checker:** compares text against a local reference database to calculate originality.
* **🤖 AI Text Detector:** analyzes writing patterns and word repetition to estimate human vs. AI probability.
* **📷 Image Metadata Wiper:** strips hidden EXIF data (GPS, Device ID, Timestamp) from images for privacy.
* **⚡ 100% Offline & Free:** No API keys required, no data collection.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML5, CSS3
* **ML & Logic:** scikit-learn (TF-IDF), Pillow (Image Processing)

---

## ⚙️ How It Works

This project uses three specialized modules to process data:

### 1️⃣ Plagiarism Detection (TF-IDF)
Instead of searching the entire internet (which requires APIs), this tool compares the input text against a set of reference documents.
* **Logic:** It converts text into vectors using **Term Frequency-Inverse Document Frequency (TF-IDF)**.
* **Calculation:** It computes the **Cosine Similarity** between the input vector and reference vectors to determine the percentage of overlap.

### 2️⃣ AI Writing Detection
AI models tend to have very specific statistical patterns (low perplexity and high consistency).
* **Logic:** The tool analyzes the text for unnatural consistency and specific word repetition patterns often found in LLM outputs.
* **Output:** It returns a probability score for "Artificial" vs "Human".

### 3️⃣ Metadata Removal
Digital images contain hidden data called EXIF.
* **Logic:** Using the **Pillow** library, the tool creates a brand new copy of the uploaded image's pixel data, discarding the EXIF container (GPS, Camera Model, etc.).
* **Output:** A clean, privacy-safe image file.

---

## 🚀 Getting Started

Follow these steps to run the project locally.

### Prerequisites
* Python 3.8+ installed

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/oasis.git](https://github.com/yourusername/oasis.git)
    cd oasis
    ```

2.  **Create a virtual environment (Optional but Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install flask scikit-learn pillow numpy
    ```

4.  **Run the application**
    ```bash
    python app.py
    ```

5.  **Open in Browser**
    Visit `http://127.0.0.1:5000` to see the app in action.

---

## 🏗️ Project Structure

```text
📂 oasis/
│
├── app.py                 # Main Flask application entry point
├── plagiarism.py          # Logic for TF-IDF and Cosine Similarity
├── ai_detector.py         # Logic for pattern analysis
├── metadata_remover.py    # Logic for EXIF stripping using Pillow
├── templates/
│   └── index.html         # Frontend interface
└── README.md              # Project documentation