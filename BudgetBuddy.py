import streamlit as st
import json
import os
import matplotlib.pyplot as plt
from uuid import uuid4

DATA_FILE = "planner_data.json"

# Inject custom CSS for personality
st.markdown("""
    <style>
    /* Set a pleasant background and custom fonts */
    .main {
        background-color: #f0f5f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h1, h2, h3, h4 {
        color: #333;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar with personality
st.sidebar.title("Bebi Budget Planner")
st.sidebar.info("""
Welcome to your fun, personalized budget planner!
Plan your savings and expenses with style. 
Create categories, add items, and see your totals update instantly.
Let's take control of your finances in a delightful way!
""")

def load_data():
    """Load saved data from a JSON file, or return a default structure if not found."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {"categories": []}

def save_data(data):
    """Save the current data to a JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def main():
    st.title("Bebi Budget Planner")
    st.write("Plan your expenses and savings while having fun!")

    # Load saved data
    data = load_data()
    if "categories" not in st.session_state:
        st.session_state.categories = data.get("categories", [])

    # --- 1) Add a New Category ---
    st.header("Add a New Category")
    with st.form("add_category_form", clear_on_submit=True):
        cat_name = st.text_input("Name (e.g., 'Cat', 'Groceries', 'Vacation')")
        cat_type = st.selectbox("Category Type", ["Saving", "Expense"])
        submitted_cat = st.form_submit_button("Add Category")
        
        if submitted_cat:
            if cat_name.strip():
                new_category = {
                    "id": str(uuid4()),
                    "name": cat_name.strip(),
                    "type": cat_type,
                    "items": []  # List to hold items for this category
                }
                st.session_state.categories.append(new_category)
                st.success(f"Awesome! Category '{cat_name}' ({cat_type}) added.")
                st.experimental_rerun()  # Force UI update immediately
            else:
                st.error("Oops! Please provide a valid category name.")

    # --- 2) Display Categories and Their Items ---
    st.header("Your Categories & Items")
    
    total_savings = 0.0
    total_expenses = 0.0

    for category in st.session_state.categories:
        with st.expander(f"{category['name']} [{category['type']}]"):
            # Calculate and display the current total for this category
            category_total = sum(item["amount"] for item in category["items"])
            st.write(f"**Current Total:** ${category_total:.2f}")
            
            # --- 2a) Add an Item to This Category ---
            with st.form(f"add_item_form_{category['id']}", clear_on_submit=True):
                item_name = st.text_input("Item Name", key=f"item_name_{category['id']}")
                # Set default value to 0.0 to avoid leftover values
                item_amount = st.number_input("Amount", min_value=0.0, value=0.0, step=1.0, key=f"item_amount_{category['id']}")
                submitted_item = st.form_submit_button("Add Item")
                
                if submitted_item:
                    if item_name.strip():
                        new_item = {
                            "id": str(uuid4()),
                            "name": item_name.strip(),
                            "amount": item_amount
                        }
                        category["items"].append(new_item)
                        st.success(f"Added '{new_item['name']}' for ${new_item['amount']:.2f}!")
                        st.experimental_rerun()  # Refresh UI immediately after adding an item
                    else:
                        st.error("Please provide a valid item name.")

            # --- 2b) List Existing Items with Edit/Remove Options ---
            if category["items"]:
                st.subheader("Manage Items")
                for item in category["items"]:
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    with col1:
                        new_name = st.text_input("Name", value=item["name"], key=f"edit_name_{item['id']}")
                    with col2:
                        new_amount = st.number_input("Amount", min_value=0.0, value=float(item["amount"]), step=1.0, key=f"edit_amount_{item['id']}")
                    with col3:
                        if st.button("Update", key=f"update_{item['id']}"):
                            item["name"] = new_name.strip()
                            item["amount"] = new_amount
                            st.success(f"Item updated to '{item['name']}' for ${item['amount']:.2f}!")
                            st.experimental_rerun()  # Refresh after updating
                    with col4:
                        if st.button("Remove", key=f"remove_{item['id']}"):
                            category["items"] = [i for i in category["items"] if i["id"] != item["id"]]
                            st.warning(f"Removed '{item['name']}'")
                            st.experimental_rerun()  # Refresh after removal

            # Update overall totals based on category type
            if category["type"] == "Saving":
                total_savings += category_total
            else:
                total_expenses += category_total

    # --- 3) Overall Summary ---
    st.header("Overall Summary")
    st.write(f"**Total Savings:** ${total_savings:.2f}")
    st.write(f"**Total Expenses:** ${total_expenses:.2f}")

    # --- 4) Pie Chart of Categories ---
    category_labels = []
    category_values = []
    for category in st.session_state.categories:
        cat_total = sum(item["amount"] for item in category["items"])
        if cat_total > 0:
            category_labels.append(f"{category['name']} ({category['type']})")
            category_values.append(cat_total)

    if category_values:
        st.subheader("Category Distribution (Pie Chart)")
        fig, ax = plt.subplots()
        ax.pie(category_values, labels=category_labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.write("No data available for the pie chart yet. Start adding some items!")

    # --- 5) Save Data Button ---
    if st.button("Save Your Planner Data"):
        data_to_save = {"categories": st.session_state.categories}
        save_data(data_to_save)
        st.success("Your data has been saved. Great work on planning your budget!")

if __name__ == "__main__":
    main()
