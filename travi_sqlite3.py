import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

current_theme = "light"


def get_table_data(conn, table_name):
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in c.fetchall()]
    c.execute(f"SELECT * FROM {table_name}")
    data = c.fetchall()
    return columns, data


def read_data_from_db(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = c.fetchall()
    table_data = {}
    for table_name in table_names:
        columns, data = get_table_data(conn, table_name[0])
        table_data[table_name[0]] = {"columns": columns, "data": data}
    conn.close()
    return table_data

def load_table_data(table_name, search=None):
    global current_db
    columns, data = get_table_data(sqlite3.connect(current_db), table_name)
    record_tree["columns"] = columns
    for col in columns:
        record_tree.heading(col, text=col)
    record_tree.delete(*record_tree.get_children())  # Clear the treeview before inserting new data
    for record in data:
        if not search:  # If the search is empty, display all records
            record_tree.insert("", "end", values=record)
        else:  # If the search is not empty, display records starting with the search text
            for value in record:
                if str(value).lower().startswith(search.lower()):
                    record_tree.insert("", "end", values=record)
                    break




def on_table_click(event):
    if not event.widget.curselection():
        return

    selected_table = event.widget.get(event.widget.curselection())
    record_tree.delete(*record_tree.get_children())
    load_table_data(selected_table)


def choose_db_file():
    global current_db
    current_db = filedialog.askopenfilename(filetypes=[("SQLite3 Database", "*.sqlite3")])
    if current_db:
        table_list.delete(0, tk.END)
        table_data = read_data_from_db(current_db)
        for table_name in table_data:
            table_list.insert(tk.END, table_name)


def execute_search():
    if not table_list.curselection():
        return

    search_text = search_entry.get()
    selected_table = table_list.get(table_list.curselection())
    record_tree.delete(*record_tree.get_children())
    if search_text.strip():  # If search_text is not empty, pass it as the search parameter
        load_table_data(selected_table, search=search_text)
    else:  # If search_text is empty, call load_table_data without the search parameter
        load_table_data(selected_table)



def refresh_data():
    if not table_list.curselection():
        return

    search_text_var.set("")  # Clear the search entry field
    selected_table = table_list.get(table_list.curselection())
    record_tree.delete(*record_tree.get_children())
    load_table_data(selected_table)  # Refresh the table data without any search parameter


def execute_sql_command():
    global current_db
    if not current_db:
        return

    conn = sqlite3.connect(current_db)
    command = sql_text_widget.get("1.0", tk.END).strip()
    if not command:
        return

    try:
        conn.execute(command)
        conn.commit()
        conn.close()
        if table_list.curselection():
            selected_table = table_list.get(table_list.curselection())
            load_table_data(selected_table)
        tk.messagebox.showinfo("Success", "SQL command executed successfully.")
    except sqlite3.Error as e:
        tk.messagebox.showerror("Error", f"An error occurred while executing the SQL command: {e}")



def toggle_theme():
    global current_theme
    if current_theme == "light":
        current_theme = "dark"
        theme_colors = {
            "bg": "black",
            "fg": "white",
            "field_bg": "gray25",
            "select_bg": "gray40"
        }
    else:
        current_theme = "light"
        theme_colors = {
            "bg": "white",
            "fg": "black",
            "field_bg": "white",
            "select_bg": "gray75"
        }

    # Update widget colors
    root.configure(bg=theme_colors["bg"])
    main_frame.configure(bg=theme_colors["bg"])
    left_frame.configure(bg=theme_colors["bg"])
    right_frame.configure(bg=theme_colors["bg"])  # This line sets the right_frame background color
    search_frame.configure(bg=theme_colors["bg"])
    bottom_frame.configure(bg=theme_colors["bg"])

    table_list.configure(bg=theme_colors["select_bg"], fg=theme_colors["fg"])

    # Add the following lines to update the Treeview style
    treeview_style = ttk.Style()
    treeview_style.configure("Treeview",
                             background=theme_colors["bg"],  # Change this line
                             fieldbackground=theme_colors["select_bg"],
                             foreground=theme_colors["fg"])

    # Remove the line below
    # record_tree.configure(bg=theme_colors["bg"])

    choose_db_btn.configure(bg=theme_colors["field_bg"], fg=theme_colors["fg"])
    search_button.configure(bg=theme_colors["field_bg"], fg=theme_colors["fg"])
    refresh_button.configure(bg=theme_colors["field_bg"], fg=theme_colors["fg"])
    execute_sql_button.configure(bg=theme_colors["field_bg"], fg=theme_colors["fg"])

    # Update widget colors for search_entry, sql_text_widget
    search_entry.configure(bg=theme_colors["field_bg"], fg=theme_colors["fg"], insertbackground=theme_colors["fg"])
    sql_text_widget.configure(bg=theme_colors["field_bg"], fg=theme_colors["fg"], insertbackground=theme_colors["fg"])




def create_gui():
    global table_list, record_tree, current_db, search_entry, search_text_var, sql_text_widget, root, main_frame, left_frame, right_frame, search_frame, bottom_frame, choose_db_btn, search_button, refresh_button, execute_sql_button
    current_db = ""

    root = tk.Tk()
    root.title("Travi_SQLite3")

    icon_image = Image.open('icon.jpg')
    icon_photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(True, icon_photo)

    # Add the theme toggle button
    theme_toggle_button = tk.Button(root, text="Toggle Theme", command=toggle_theme)
    theme_toggle_button.pack()

    # rest of the code remains the same



    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)

    table_list = tk.Listbox(left_frame, width=30)
    table_list.pack(fill=tk.BOTH, expand=True)
    table_list.bind("<<ListboxSelect>>", on_table_click)

    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    search_frame = tk.Frame(right_frame)
    search_frame.pack()

    search_text_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_text_var)
    search_entry.pack(side=tk.LEFT)

    search_button = tk.Button(search_frame, text="Search", command=execute_search)
    search_button.pack(side=tk.LEFT)

    refresh_button = tk.Button(search_frame, text="Refresh", command=refresh_data)
    refresh_button.pack(side=tk.LEFT)

    record_tree = ttk.Treeview(right_frame, show="headings")
    record_tree.pack(fill=tk.BOTH, expand=True)

    choose_db_btn = tk.Button(left_frame, text="Choose Database", command=choose_db_file)
    choose_db_btn.pack()

    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

    sql_text_widget = tk.Text(bottom_frame, wrap=tk.WORD, height=5)
    sql_text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

    execute_sql_button = tk.Button(bottom_frame, text="Execute SQL", command=execute_sql_command)
    execute_sql_button.pack(side=tk.RIGHT)

    root.mainloop()




if __name__ == "__main__":
    create_gui()
