# 🏏 BCCI Cricket Statistics Analysis

A comprehensive cricket statistics analysis project that **scrapes BCCI data**, stores it in a **Neon database**, and provides **analytical queries**.

---

## 🚀 Complete Setup & Execution

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/pradeepacharya123/BCCI_ANALYSIS_TASK.git
cd BCCI_ANALYSIS_TASK

# Create Virtual Environment
python -m venv venv

# Activate Virtual Environment
venv\Scripts\activate       # On Windows
# or
source venv/bin/activate    # On Mac/Linux

# Install required dependencies
pip install -r requirements.txt

#In the project root, create a file named .env (note the dot at the beginning). Then open it and add the following line:
DATABASE_URL=your_neon_database_connection_string_here


# Run All Scripts Orderly
python test_odi_batting.py
python test_odi_bowling.py
python create_table.py
python insert.py
python query.py
