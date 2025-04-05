**Food Waste Tracker**
A simple Python application that helps users track food waste, provides reduction tips, and generates weekly summaries of food waste. This project uses SQLite for data storage and allows users to register, log food waste, and view summaries of their waste patterns.

**Features**
User Registration and Authentication: Allows users to register with a username and password, and log in to track their food waste.

**Food Waste Logging:** Users can log food waste by specifying the food item and quantity wasted.

**Weekly Summary:** Generates a weekly summary of the food items wasted and the total quantity for each.

**Reduction Tips:** Provides tips on how to reduce food waste for specific food items.

**Data Visualization:** Displays a bar chart representing the weekly food waste data.

**Requirements**
Python 3.x
SQLite (comes pre-installed with Python)
Matplotlib (for data visualization)

You can install Matplotlib by running:
    pip install matplotlib
    
**Setup**

**Clone the repository to your local machine:**
git clone https://github.com/vineet1603/food-waste-tracker.git
cd food-waste-tracker

Install the required dependencies (Matplotlib):

pip install matplotlib

**Run the application:**

python food_waste_tracker.py

**Usage**
**1. Registration and Login**
When you first run the program, you will be prompted to either register or log in.

**Register:** Create a new account with a unique username and password.

**Login:** Log in with an existing account.

**2. Logging Food Waste**
    Once logged in, you can log food waste:
    Enter the food item that you wasted.
    Specify the quantity of the food waste (in kilograms).

**3. Weekly Summary**
You can view a summary of your food waste for the past week, including the total quantity wasted for each food item. A bar chart will be displayed as a visual representation of the waste data.

**4. Food Waste Reduction Tips**
After logging a food waste entry, the program will provide tips on how to reduce waste for that food item (e.g., freezing bread, repurposing vegetables, etc.).

