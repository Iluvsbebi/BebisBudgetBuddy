import streamlit as st
import json
import os
import matplotlib.pyplot as plt

DATA_FILE = 'budget_data.json'

def load_budget():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {'income': 0.0, 'expenses': []}

def save_budget(budget_data):
    with open(DATA_FILE, 'w') as file:
        json.dump(budget_data, file, indent=4)

def main():
    st.title("Bebi Budget Buddy")
    
    # Load saved data (if any)
    budget_data = load_budget()
    
    # Initialize session state variables
    if 'income' not in st.session_state:
        st.session_state.income = budget_data.get('income', 0.0)
    if 'expenses' not in st.session_state:
        st.session_state.expenses = budget_data.get('expenses', [])
    
    # Income Input
    st.header("Set Your Monthly Income")
    income_input = st.number_input("Monthly Income", value=st.session_state.income, step=100.0)
    st.session_state.income = income_input

    # Expense Input Form
    st.header("Add an Expense")
    with st.form("expense_form", clear_on_submit=True):
        expense_name = st.text_input("Expense Name")
        expense_amount = st.number_input("Expense Amount", min_value=0.0, step=1.0)
        expense_category = st.text_input("Expense Category (Label)")
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            if expense_name and expense_category:
                expense = {
                    'name': expense_name,
                    'amount': expense_amount,
                    'category': expense_category
                }
                st.session_state.expenses.append(expense)
                st.success(f"Added: {expense_name} (${expense_amount:.2f}) in category '{expense_category}'")
            else:
                st.error("Please enter both an expense name and a category.")
    
    # Display Expense List
    st.header("Expense List")
    if st.session_state.expenses:
        for expense in st.session_state.expenses:
            st.write(f"{expense['name']} - ${expense['amount']:.2f} ({expense['category']})")
    else:
        st.write("No expenses added yet.")

    # Aggregate expenses by category
    category_totals = {}
    for expense in st.session_state.expenses:
        cat = expense['category']
        category_totals[cat] = category_totals.get(cat, 0) + expense['amount']

    # Calculate overall totals
    total_expenses = sum(exp['amount'] for exp in st.session_state.expenses)
    savings = st.session_state.income - total_expenses

    st.header("Budget Summary")
    st.write(f"**Total Income:** ${st.session_state.income:.2f}")
    st.write(f"**Total Expenses:** ${total_expenses:.2f}")
    st.write(f"**Savings:** ${savings:.2f}")

    # Chart: Expenses by Category
    if category_totals:
        st.subheader("Expenses by Category")
        fig, ax = plt.subplots()
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        ax.bar(categories, amounts)
        ax.set_ylabel("Amount")
        ax.set_title("Expenses by Category")
        st.pyplot(fig)

    # Chart: Overall Budget Overview
    st.subheader("Overall Budget Overview")
    fig2, ax2 = plt.subplots()
    labels = ['Income', 'Expenses', 'Savings']
    values = [st.session_state.income, total_expenses, savings]
    ax2.bar(labels, values)
    ax2.set_ylabel("Amount")
    ax2.set_title("Income vs. Expenses vs. Savings")
    st.pyplot(fig2)

    # Save Data Button
    if st.button("Save Budget Data"):
        data_to_save = {
            'income': st.session_state.income,
            'expenses': st.session_state.expenses
        }
        save_budget(data_to_save)
        st.success("Budget data saved successfully!")

if __name__ == '__main__':
    main()
