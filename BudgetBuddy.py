import streamlit as st
import json
import os
import matplotlib.pyplot as plt
from uuid import uuid4

DATA_FILE = "planner_data.json"

def load_data():
    """Load saved data from a JSON file, or return a default structure if not found."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {"categories": []}

def save_data(data):
    """Save the current data to a JSON file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    st.title("Bebi's Budget Planner")

    # Load data or initialize structure
    data = load_data()
    
    # Use session_state to avoid reloading data on every interaction
    if "categories" not in st.session_state:
        st.session_state.categories = data.get("categories", [])
    
    # 1) Add a new category
    st.header("Add a New Category")
    with st.form("add_category_form", clear_on_submit=True):
        cat_name = st.text_input("Name (e.g., 'Cat', 'Groceries', 'Vacation')")
        cat_type = st.selectbox("Category Type", ["Saving", "Expense"])
        submitted_cat = st.form_submit_button("Add Category")
        
        if submitted_cat:
            if cat_name.strip():
                new_category = {
                    "id": str(uuid4()),        # Unique ID for the category
                    "name": cat_name.strip(),
                    "type": cat_type,
                    "items": []                # List of items under this category
                }
                st.session_state.categories.append(new_category)
                st.success(f"Added category: {cat_name} ({cat_type})")
            else:
                st.error("Please provide a valid category name.")
    
    # 2) Display each category in an expander, allow adding items
    st.header("Categories and Their Items")
    
    # For calculating overall totals later
    total_savings = 0.0
    total_expenses = 0.0

    for category in st.session_state.categories:
        with st.expander(f"{category['name']} [{category['type']}]"):
            
            # Calculate the current total for this category
            category_total = sum(item["amount"] for item in category["items"])
            st.write(f"**Current Total:** ${category_total:.2f}")
            
            # Add item form
            with st.form(f"add_item_form_{category['id']}", clear_on_submit=True):
                item_name = st.text_input("Item Name", key=f"item_name_{category['id']}")
                item_amount = st.number_input("Amount", min_value=0.0, step=1.0, key=f"item_amount_{category['id']}")
                submitted_item = st.form_submit_button("Add Item")
                
                if submitted_item:
                    if item_name.strip():
                        new_item = {
                            "id": str(uuid4()),   # Unique ID for the item
                            "name": item_name.strip(),
                            "amount": item_amount
                        }
                        category["items"].append(new_item)
                        st.success(f"Added item: {item_name} (${item_amount:.2f})")
                    else:
                        st.error("Please provide a valid item name.")
            
            # List items, allow editing/removal
            if category["items"]:
                st.subheader("Items")
                for item in category["items"]:
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    with col1:
                        new_name = st.text_input("Name", value=item["name"], key=f"edit_name_{item['id']}")
                    with col2:
                        new_amount = st.number_input(
                            "Amount", 
                            min_value=0.0, 
                            value=float(item["amount"]), 
                            step=1.0, 
                            key=f"edit_amount_{item['id']}"
                        )
                    with col3:
                        # Update (edit) button
                        if st.button("Update", key=f"update_{item['id']}"):
                            item["name"] = new_name.strip()
                            item["amount"] = new_amount
                            st.success(f"Updated item: {item['name']} (${item['amount']:.2f})")
                    with col4:
                        # Remove (delete) button
                        if st.button("Remove", key=f"remove_{item['id']}"):
                            category["items"] = [i for i in category["items"] if i["id"] != item["id"]]
                            st.warning(f"Removed item: {item['name']}")
                            st.experimental_rerun()
            
            # Update overall totals
            if category["type"] == "Saving":
                total_savings += category_total
            else:
                total_expenses += category_total

    # 3) Display overall summary
    st.header("Overall Summary")
    st.write(f"**Total Savings:** ${total_savings:.2f}")
    st.write(f"**Total Expenses:** ${total_expenses:.2f}")
    
    # 4) Pie Chart of Categories (by total amount)
    #    We only plot categories that have a non-zero total
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
        st.write("No category data to display in the pie chart yet.")

    # 5) Save Data Button
    if st.button("Save Planner Data"):
        data_to_save = {"categories": st.session_state.categories}
        save_data(data_to_save)
        st.success("Data saved successfully!")

if __name__ == "__main__":
    main()
