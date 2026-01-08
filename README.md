# H&M Web Scraper & Market Analysis 👖📊
👉 **Full project explanation available on my blog:**  
🔗 [Click here](https://dataineverywhere.ct.ws/projects/building-a-web-scraper-for-market-analysis/)

![Project Status](https://img.shields.io/badge/Status-Complete-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Lib](https://img.shields.io/badge/Library-BeautifulSoup%20%7C%20Pandas-orange)

## 📋 Table of Contents
* [Business Problem](#-business-problem)
* [Solution Strategy](#-solution-strategy)
* [Technical Architecture](#-technical-architecture)
* [Technologies Used](#-technologies-used)
* [Data Engineering Steps](#-data-engineering-steps)
* [Key Insights](#-key-insights)
* [How to Run](#-how-to-run)
* [Author](#-author)

---

## 💼 Business Problem
"Start Jeans" is a new e-commerce venture by entrepreneurs Eduardo and Marcelo, aiming to enter the US fashion market focusing on **Men's Jeans**. To minimize risk and define a competitive Minimum Viable Product (MVP), the partners needed data-driven answers to three key questions:

1.  **Price:** What is the optimal entry price?
2.  **Inventory:** Which colors and models should be prioritized?
3.  **Production:** What is the specific material composition (Cotton/Elastane ratio) required to match market standards?

This project solves this problem by building an automated **Web Scraper** to collect, clean, and analyze data from a major competitor (H&M).



---

## 🚀 Solution Strategy
The solution was designed as a robust **ETL (Extract, Transform, Load)** pipeline:

1.  **Extraction:** A bot navigates the H&M Men's Jeans category. It iterates through every product and, crucially, opens every **color variant** to scrape specific details.
2.  **Transformation:** Raw text (e.g., *"Shell: Cotton 98%, Spandex 2%"*) is parsed using **Regex** to split materials into distinct columns (Cotton, Polyester, Elastane).
3.  **Loading:** Clean data is stored in a **SQLite** database for analysis.
4.  **Analysis:** SQL queries and Python visualization libraries are used to generate business insights.

---

## 🏗 Technical Architecture



The system consists of three main modules:
* **Data Collection:** Uses `requests` and `BeautifulSoup` to parse HTML.
* **Data Cleaning:** Uses `pandas` for manipulation and `re` (Regular Expressions) for string parsing.
* **Storage:** Uses `sqlalchemy` and `sqlite3` to manage the database `database_hm.sqlite`.

---

## 🛠 Technologies Used
* **Language:** Python 3.x
* **Web Scraping:** BeautifulSoup4, Requests
* **Data Manipulation:** Pandas, NumPy
* **Database:** SQLite, SQLAlchemy
* **Utils:** Logging, DateTime, OS, Re (Regex)

---

## ⚙️ Data Engineering Steps

### 1. Data Collection (The "Deep Dive")
The scraper does not stop at the showroom page. It implements a nested loop strategy:
* **Loop 1:** Collects all Product IDs from the main gallery.
* **Loop 2:** Accesses each Product Page.
* **Loop 3:** Identifies all available **Color IDs** within that product and scrapes the specific composition for *that* color.

### 2. Data Cleaning & Regex
The raw material data is unstructured. A custom cleaning function was built to:
* Remove formatting characters (`\n`, `\t`).
* Standardize column names to `snake_case`.
* **Parse Composition:**
    * Input: `Cotton 98%, Elastane 2%`
    * Output: `col_cotton: 0.98`, `col_elastane: 0.02`

---

## 📊 Key Insights
Based on the data collected in the `vitrine` table:

1.  **Optimal Price:** The majority of competitors' products are priced between **$29.99 and $39.99**.
    * *Recommendation:* Start Jeans should launch at **$29.99**.
2.  **Inventory Strategy:** **Denim Blue** and **Black** cover >60% of the market.
    * *Recommendation:* Avoid niche colors (Gray, White) for the MVP.
3.  **Material Composition:** 100% Cotton is rare. The market standard for "Comfort Fit" is **98% Cotton / 2% Elastane**.


---

## 💻 How to Run

### Prerequisites
* Python 3.8+
* Pip

### Installation
1.  Clone this repository:
    ```bash
    git clone [https://github.com/yourusername/hm-web-scraper.git](https://github.com/yourusername/hm-web-scraper.git)
    ```
2.  Install requirements:
    ```bash
    pip install pandas requests beautifulsoup4 sqlalchemy
    ```

### Execution
Run the main script to start the scraping process:
```bash
python webscraping_hm.py
