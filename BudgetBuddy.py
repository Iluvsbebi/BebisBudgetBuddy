import streamlit as st
import json
import os
import matplotlib.pyplot as plt

DATA_FILE = 'planner_data.json'

def load_data():
    """Load saved data from a JSON file, or return an empty structure if not found."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {"entries": []}

def save_data(data):
    """Save the current data to a JSON file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    st.title("Bebi Budget Planner")

    # Load or initialize data
    data = load_data()
    if "entries" not in st.session_state:
        st.session_state.entries = data.get("entries", [])

    # -----------------------------
    # 1) Add a Category Section
    # -----------------------------
    st.header("Add a Category")
    with st.form("add_category_form", clear_on_submit=True):
        name = st.text_input("Name")  # e.g., 'Groceries', 'Rent', 'Vacation', etc.
        category_type = st.selectbox("Category (Saving or Expense)", ["Saving", "Expense"])
        amount = st.number_input("Amount", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Add")
        
        if submitted:
            if name.strip():
                # Store each entry as a dictionary
                entry = {
                    "name": name.strip(),
                    "type": category_type,
                    "amount": amount
                }
                st.session_state.entries.append(entry)
                st.success(f"Added: {name} (${amount:.2f}) as {category_type}")
            else:
                st.error("Please provide a valid Name.")

    # -----------------------------
    # 2) Display Entries
    # -----------------------------
    st.header("Current Entries")
    if st.session_state.entries:
        for i, entry in enumerate(st.session_state.entries, start=1):
            st.write(
                f"**{i}.** Name: {entry['name']} | "
                f"Category: {entry['type']} | "
                f"Amount: ${entry['amount']:.2f}"
            )
    else:
        st.write("No entries yet.")

    # -----------------------------
    # 3) Create Pie Charts
    # -----------------------------
    if st.session_state.entries:
        # Separate data into Saving vs. Expense
        savings = [e for e in st.session_state.entries if e['type'] == 'Saving']
        expenses = [e for e in st.session_state.entries if e['type'] == 'Expense']
        
        total_savings = sum(e['amount'] for e in savings)
        total_expenses = sum(e['amount'] for e in expenses)
        
        st.header("Pie Charts")
        
        # Pie Chart 1: Distribution by Name (All entries together)
        st.subheader("Distribution by Name")
        fig1, ax1 = plt.subplots()
        # Aggregate amounts by name
        name_amounts = {}
        for e in st.session_state.entries:
            name_amounts[e['name']] = name_amounts.get(e['name'], 0) + e['amount']
        labels1 = list(name_amounts.keys())
        values1 = list(name_amounts.values())
        
        ax1.pie(values1, labels=labels1, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')  # Ensure the pie chart is circular
        st.pyplot(fig1)
        
        # Pie Chart 2: Saving vs. Expense
        st.subheader("Savings vs. Expenses")
        if total_savings == 0 and total_expenses == 0:
            st.write("No data to display in this pie chart yet.")
        else:
            fig2, ax2 = plt.subplots()
            labels2 = ["Saving", "Expense"]
            values2 = [total_savings, total_expenses]
            
            ax2.pie(values2, labels=labels2, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            st.pyplot(fig2)

    # -----------------------------
    # 4) Save Data
    # -----------------------------
    if st.button("Save Planner Data"):
        data_to_save = {"entries": st.session_state.entries}
        save_data(data_to_save)
        st.success("Data saved successfully!")

if __name__ == "__main__":
    main()
