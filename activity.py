import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# tkinter: Used for creating a GUI in Python.
# ttk provides themed widgets for a modern look.
# messagebox: For showing pop-up dialogs (e.g., alerts).
# Enables connecting and interacting with a MySQL database.

# Establishing the connection
conn = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='StudGrades')

# Function to refresh the dropdown menu and display data
def refresh_data():c
    cursor = conn.cursor()
    cursor.execute("SELECT ID FROM products")

    # row[0] refers to the first (and only) element of each tuple, which corresponds to the ID column value.

    ids = [row[0] for row in cursor.fetchall()]

    # Retrieves all rows from the query result using fetchall().
    # Extracts the first element (row[0]) from each row (the ID value) and stores it in a list called ids.

    dropdown_id['values'] = ids

    # Sets the ids list as the available options (values) in the ttk.Combobox dropdown_id.

    # Refresh the table
    display_data()
    cursor.close()


# Function to display all data in the table
def display_data():
    # Retrieves all the child items (rows) currently displayed in the treeview widget (tree).
    # Loops through each row (identified by its item ID) in the treeview.

    for i in tree.get_children():
        tree.delete(i)

    # Deletes the corresponding row/item from the treeview using its item ID (i).

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)

        """Inserts a new item into the Treeview widget (tree).
    "": Specifies that the new row has no parent (it's added at the top level).
    tk.END: Appends the new item at the end of the Treeview.
    values=row: Sets the content of the row using the values in the row object."""

    cursor.close()


# Function to search a record by Product ID and fill entries


def search_record():
    search_id = dropdown_id.get()

    if not search_id:
        messagebox.showerror("Error", "Please select or enter a Product ID to search!")
        return

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM products WHERE ID = %s", (search_id,))
        row = cursor.fetchone()
        # Checks if a row (result from a database or data structure) is not empty (i.e., it contains data).
        if row:
            # Clears any existing text in the entry_name input field (from index 0 to the end).
            entry_name.delete(0, tk.END)
            entry_name.insert(0, row[1])  # Product Name
            entry_price.delete(0, tk.END)
            entry_price.insert(0, row[2])  # Price
            entry_quantity.delete(0, tk.END)
            entry_quantity.insert(0, row[3])  # Quantity
        else:
            messagebox.showinfo("No Results", f"No record found with Product ID {search_id}")

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error searching record: {err}")
    finally:
        cursor.close()


# Function to search for records by Product Name and display them in the table
def search_table():
    product_name = entry_search_name.get()
    if not product_name:
        messagebox.showerror("Error", "Please enter a Product Name to search!")
        return

    for i in tree.get_children():
        tree.delete(i)

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM products WHERE PRODUCT_NAME LIKE %s", (f"%{product_name}%",))
        rows = cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        if not rows:
            messagebox.showinfo("No Results", f"No records found with Product Name containing '{product_name}'")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error searching records: {err}")
    finally:
        cursor.close()


# Function to add a new record
def add_record():
    name = entry_name.get()
    price = entry_price.get()
    quantity = entry_quantity.get()

    if not name or not price or not quantity:
        messagebox.showerror("Error", "All fields are required!")
        return

    if not price.isdigit() or not quantity.isdigit():
        messagebox.showerror("Error", "Price and Quantity must be numeric!")
        return

    sql = "INSERT INTO products (PRODUCT_NAME, PRICE, QUANTITY, MANUFACTURER) VALUES (%s, %s, %s)"
    values = (name, price, quantity, mam)

    cursor = conn.cursor()
    try:
        cursor.execute(sql, values)
        conn.commit()
        messagebox.showinfo("Success", "Record added successfully!")
        refresh_data()
    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Error", f"Failed to add record: {err}")
    finally:
        cursor.close()


# Function to update the selected record
def update_record():
    selected_id = dropdown_id.get()
    name = entry_name.get()
    price = entry_price.get()
    quantity = entry_quantity.get()

    if not selected_id:
        messagebox.showerror("Error", "No Product ID selected!")
        return

    if not name or not price or not quantity:
        messagebox.showerror("Error", "All fields are required!")
        return

    if not price.isdigit() or not quantity.isdigit():
        messagebox.showerror("Error", "Price and Quantity must be numeric!")
        return

    sql = "UPDATE products SET PRODUCT_NAME=%s, PRICE=%s, QUANTITY=%s, MANUFACTURER=%s WHERE ID=%s"
    values = (name, price, quantity, manufacturer, selected_id)

    cursor = conn.cursor()
    try:
        cursor.execute(sql, values)
        conn.commit()
        messagebox.showinfo("Success", "Record updated successfully!")
        refresh_data()
    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Error", f"Failed to update record: {err}")
    finally:
        cursor.close()


# Function to delete the selected record with confirmation
def delete_record():
    selected_id = dropdown_id.get()
    if not selected_id:
        messagebox.showerror("Error", "No Product ID selected!")
        return

    # Ask for confirmation before deleting
    confirm = messagebox.askyesno("Confirm Delete",
                                  f"Are you sure you want to delete the record with ID {selected_id}?")
    if not confirm:
        return

    sql = "DELETE FROM products WHERE ID=%s"
    cursor = conn.cursor()
    try:
        # We enclose selected_id in (,) to create a tuple, as cursor.execute() requires parameters to be passed as a sequence.
        # tuple is an ordered, immutable collection of elements in Python, defined using parentheses (), and can contain multiple values of different data types. Example: my_tuple = (1, 'apple', 3.14).
        cursor.execute(sql, (selected_id,))
        conn.commit()
        messagebox.showinfo("Success", "Record deleted successfully!")
        refresh_data()
    except mysql.connector.Error as err:
        # conn.rollback() undoes any changes made to the database since the last commit, effectively canceling any uncommitted transactions.
        conn.rollback()
        messagebox.showerror("Error", f"Failed to delete record: {err}")
    finally:
        cursor.close()


# Tkinter GUI
root = tk.Tk()
root.title("Python CRUD Application")
root.geometry("900x750")
root.resizable(False, False)

# Application Title
title_label = tk.Label(root, text="CRUD Application", font=("Arial", 18, "bold"), pady=10)
title_label.pack()

# Frame for input fields
frame_inputs = ttk.LabelFrame(root, text="Product Information", padding=(50, 10))
frame_inputs.pack(fill="x", padx=10, pady=10)
# fill="x": Expands the frame horizontally to fill the available width in the parent widget (root).

ttk.Label(frame_inputs, text="Product Name:").grid(row=0, column=0, padx=5, pady=5)
entry_name = ttk.Entry(frame_inputs)
entry_name.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_inputs, text="Product Price:").grid(row=0, column=2, padx=5, pady=5)
entry_price = ttk.Entry(frame_inputs)
entry_price.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(frame_inputs, text="Product Quantity:").grid(row=0, column=4, padx=5, pady=5)
entry_quantity = ttk.Entry(frame_inputs)
entry_quantity.grid(row=0, column=5, padx=5, pady=5)

ttk.Label(frame_inputs, text="Product ID:").grid(row=1, column=0, padx=5, pady=5)
dropdown_id = ttk.Combobox(frame_inputs, state="readonly")
dropdown_id.grid(row=1, column=1, padx=5, pady=5)

ttk.Button(frame_inputs, text="Search by ID", command=search_record).grid(row=1, column=2, padx=5, pady=5)

ttk.Label(frame_inputs, text="Search Product Name:").grid(row=1, column=3, padx=5, pady=5)
entry_search_name = ttk.Entry(frame_inputs)
entry_search_name.grid(row=1, column=4, padx=5, pady=5)

ttk.Button(frame_inputs, text="Search Table", command=search_table).grid(row=1, column=5, padx=5, pady=5)

ttk.Label(frame_inputs, text="Manufacturer:").grid(row=2, column=1, padx=5, pady=5)
entry_quantity = ttk.Entry(frame_inputs)
entry_quantity.grid(row=2, column=0, padx=5, pady=5)

# Frame for action buttons
frame_actions = ttk.Frame(root)
frame_actions.pack(fill="x", padx=10, pady=10)
# This frame is likely intended to group buttons in a clean, organized layout.

ttk.Button(frame_actions, text="Add", command=add_record).grid(row=0, column=0, padx=10, pady=10)
ttk.Button(frame_actions, text="Update", command=update_record).grid(row=0, column=1, padx=10, pady=10)
ttk.Button(frame_actions, text="Delete", command=delete_record).grid(row=0, column=2, padx=10, pady=10)

# Frame for the table
frame_table = ttk.LabelFrame(root, text="Product Table", padding=(10, 10))
frame_table.pack(fill="both", expand=True, padx=10, pady=10)
# expand=True: Ensures the frame expands to take up extra space if the parent widget (window) is resized.
# fill="both": Expands the frame to fill both the horizontal and vertical space in the parent widget.

columns = ("ID", "Product Name", "Price", "Quantity", "Manufacturer")

'''show="headings": Table-like view without hierarchy.
show="tree headings": Treeview with column headers and hierarchy.
show="tree": Hierarchical tree structure without column headers.'''

'''"browse": For single-row selection, e.g., editing or viewing details of a single item.
"extended": For multi-selection scenarios, e.g., bulk operations.
"none": For read-only views where selection isn't required.
"multiple": For non-contiguous row selections without requiring keyboard modifiers.'''

tree = ttk.Treeview(frame_table, columns=columns, show="headings", selectmode="browse")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(fill="both", expand=True)

"""command=tree.yview: Links the scrollbar's movement to the vertical scrolling action of the Treeview."""
scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")
"""side="right": Aligns the scrollbar to the right edge of the frame.
fill="y": Ensures the scrollbar stretches to fill the vertical height of the frame."""
# Initial data load
refresh_data()

# Run the Tkinter event loop
root.mainloop()
