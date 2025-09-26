# Problem Statement: Cricket Statistics

The goal of this assignment is to **scrape, store, and analyze international cricket statistics** from the official BCCI website and perform specific queries to extract meaningful insights.

---

## 📌 Prerequisites

* **Python 3.8+**
* **VS Code** (or any IDE of your choice)

---

## ⚙️ Tech Stack

* **Python**
* **PostgreSQL** (Neon DB or any cloud database)

---

## ✅ Tasks

### **1. Data Collection**

1. Visit **[BCCI International Stats](https://www.bcci.tv/international/men/stats)**.
2. Navigate to the **Stats** section.
3. Collect data for both formats:

   * **Test**
   * **ODI**
4. Scrape the following datasets:

   * **Batting Records** → Most Runs
   * **Bowling Records** → Most Wickets
5. Export the scraped data into **CSV files**

---

### **2. Database Design & Storage**

1. Design a **normalized database schema** to store the scraped data.

   * Follow **DB normalization rules** (at least up to **3NF**).
   * Include **relationships** between players, formats, batting stats, and bowling stats.
2. Insert the CSV data into the database.

---

### **3. Queries & Analysis**

Once the data is stored in the database, perform the following:

#### 🔎 Search Functionality

* Find all players whose names start with `"V"`.
* Search for a player by **exact name**.

#### 📊 Match Records

* Find the player who has played the **highest number of matches**.
* Find the player who has played the **lowest number of matches**.

#### 🏏 Performance Insights

* Identify the **Top 5 Best Bowlers**.
* Identify the **Top 5 Best Batsmen**.
* Determine the **most aggressive batsman** (based on **strike rate / scoring rate**).
* Identify players who can be considered **All-Rounders** (strong in both batting and bowling).

#### ⚔️ Custom Player Comparisons

* How many more matches does **Rohit** need to play to surpass **Virat’s** match record?
* How many additional matches does **Harbhajan Singh** need to play to reach the **5th position** in most matches played?

---

## 📦 Deliverables

* **CSV files** for Test & ODI (Batting and Bowling).
* **Database Schema Design** (ER diagram + explanation).
* **SQL queries** for each analysis task.
* **Results/Outputs** of the queries (in terminal/command line).

---

## 🚀 Getting Started

### Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/Shashank-Salian/tb-task.git
cd tb-task
```

---

### 📦 Installation Command

To install all the required packages, run the following command in your terminal:

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup (Neon DB Example)

1. Sign up at [neon.com](https://neon.com/) (free PostgreSQL cloud service).
2. Create a new **database project**.
3. Copy the connection string (`DATABASE_URL`) from your dashboard.
4. Use this connection string in your Python scripts to connect and insert data.

---

## ❓ Questions to Answer

1. **Search Functionality**

   * List all players whose names start with `"V"`.
   * Find a player by exact name.

2. **Match Records**

   * Who has played the **highest number of matches**?
   * Who has played the **lowest number of matches**?

3. **Performance Insights**

   * Who are the **Top 5 Best Bowlers**?
   * Who are the **Top 5 Best Batsmen**?
   * Who is the **most aggressive batsman**?
   * Which players qualify as **All-Rounders**?

4. **Custom Player Comparisons**

   * How many more matches does **Rohit** need to play to surpass **Virat’s** match record?
   * How many more matches does **Harbhajan Singh** need to play to reach **5th place** in matches played?

