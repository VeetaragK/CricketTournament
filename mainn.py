import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from db import connect_to_database

# === Connect to database ===
conn = connect_to_database()
cursor = conn.cursor()

# === Main Window ===
root = ttk.Window(themename="darkly")
root.title("Cricket Player Management System")
root.geometry("1200x850")
root.state('zoomed')

# === Background Image ===
try:
    bg_image = Image.open("background.jpg").resize((1920, 1080), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = ttk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print("Background not loaded:", e)

# === Scrollable Canvas ===
canvas = tk.Canvas(root, highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def resize_canvas(event):
    canvas.itemconfig(canvas_frame, width=event.width)

canvas.bind("<Configure>", resize_canvas)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# === Variables ===
name_var = tk.StringVar()
role_var = tk.StringVar()
age_var = tk.StringVar()
country_var = tk.StringVar()
team_name_var = tk.StringVar()
bowling_role_var = tk.StringVar()
team_logo_path = tk.StringVar()
player_photo_path = tk.StringVar()
selected_player_name = tk.StringVar()
format_var = tk.StringVar(value="ODI")
runs_var = tk.StringVar()
balls_var = tk.StringVar()
sixes_var = tk.StringVar()
fours_var = tk.StringVar()
wickets_var = tk.StringVar()
balls_bowled_var = tk.StringVar()
figures_var = tk.StringVar()

# === Utility Functions ===
def upload_image(path_var, label=None):
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if path:
        path_var.set(path)
        if label:
            img = Image.open(path).resize((100, 100))
            img = ImageTk.PhotoImage(img)
            label.config(image=img)
            label.image = img

def reset_fields():
    for var in [name_var, role_var, age_var, country_var, team_name_var, bowling_role_var,
                team_logo_path, player_photo_path, selected_player_name,
                runs_var, balls_var, sixes_var, fours_var, wickets_var, balls_bowled_var, figures_var]:
        var.set("")
    format_var.set("ODI")
    update_player_names()

def register_player():
    try:
        cursor.execute("""
            INSERT INTO players (name, role, age, country, team_name, bowling_role, team_logo_path, player_photo_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name_var.get(), role_var.get(), int(age_var.get()), country_var.get(), team_name_var.get(),
            bowling_role_var.get(), team_logo_path.get(), player_photo_path.get()
        ))
        conn.commit()
        messagebox.showinfo("Success", "Player registered!")
        reset_fields()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_player_names():
    cursor.execute("SELECT name FROM players")
    names = [row[0] for row in cursor.fetchall()]
    player_dropdown['values'] = names

def get_player_id_by_name(name):
    cursor.execute("SELECT player_id FROM players WHERE name = %s", (name,))
    result = cursor.fetchone()
    return result[0] if result else None

def add_match_performance():
    player_id = get_player_id_by_name(selected_player_name.get())
    if not player_id:
        messagebox.showerror("Error", "Player not found.")
        return
    try:
        cursor.execute("""
            INSERT INTO matches (player_id, match_format, runs_scored, balls_faced, sixes, fours,
            wickets_taken, balls_bowled, best_figures)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            player_id, format_var.get(), int(runs_var.get()), int(balls_var.get()),
            int(sixes_var.get()), int(fours_var.get()), int(wickets_var.get()),
            int(balls_bowled_var.get()), figures_var.get()
        ))
        conn.commit()
        messagebox.showinfo("Success", "Performance added!")
        reset_fields()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# === Tabs ===
notebook = ttk.Notebook(scrollable_frame)
notebook.pack(fill="both", expand=True, padx=20, pady=20)

register_tab = ttk.Frame(notebook)
performance_tab = ttk.Frame(notebook)
notebook.add(register_tab, text="Register Player")
notebook.add(performance_tab, text="Add Performance")

# === Register Tab ===
register_frame = ttk.LabelFrame(register_tab, text="Player Information", padding=20)
register_frame.pack(padx=20, pady=20, fill="both", expand=True)

register_frame.columnconfigure(0, weight=1)  # Spacer
register_frame.columnconfigure(1, weight=0)  # Form Left
register_frame.columnconfigure(2, weight=0)  # Form Right
register_frame.columnconfigure(3, weight=1)  # Spacer

fields = [("Name", name_var), ("Role", role_var), ("Age", age_var),
          ("Country", country_var), ("Team", team_name_var), ("Bowling Role", bowling_role_var)]

for i, (label, var) in enumerate(fields):
    ttk.Label(register_frame, text=label).grid(row=i, column=1, sticky="e", padx=10, pady=10)
    ttk.Entry(register_frame, textvariable=var).grid(row=i, column=2, padx=10, pady=10)

ttk.Button(register_frame, text="Upload Team Logo", command=lambda: upload_image(team_logo_path)).grid(
    row=6, column=1, columnspan=2, pady=10)

ttk.Button(register_frame, text="Upload Player Photo", command=lambda: upload_image(player_photo_path)).grid(
    row=7, column=1, columnspan=2, pady=10)

ttk.Button(register_frame, text="Register Player", bootstyle="success", command=register_player).grid(
    row=8, column=1, columnspan=2, pady=20)


# === Performance Tab ===
performance_frame = ttk.LabelFrame(performance_tab, text="Match Performance", padding=20)
performance_frame.pack(padx=20, pady=20, fill="both", expand=True)

performance_frame.columnconfigure(0, weight=1)
performance_frame.columnconfigure(1, weight=0)
performance_frame.columnconfigure(2, weight=0)
performance_frame.columnconfigure(3, weight=1)

perf_fields = [("Runs", runs_var), ("Balls Faced", balls_var), ("Sixes", sixes_var),
               ("Fours", fours_var), ("Wickets", wickets_var),
               ("Balls Bowled", balls_bowled_var), ("Best Figures", figures_var)]

for i, (label, var) in enumerate(perf_fields):
    ttk.Label(performance_frame, text=label).grid(row=i, column=1, sticky="e", padx=10, pady=10)
    ttk.Entry(performance_frame, textvariable=var).grid(row=i, column=2, padx=10, pady=10)

ttk.Label(performance_frame, text="Select Player").grid(row=len(perf_fields), column=1, sticky="e", padx=10, pady=10)
player_dropdown = ttk.Combobox(performance_frame, textvariable=selected_player_name)
player_dropdown.grid(row=len(perf_fields), column=2, padx=10, pady=10)

ttk.Label(performance_frame, text="Match Format").grid(row=len(perf_fields)+1, column=1, sticky="e", padx=10, pady=10)
ttk.Combobox(performance_frame, textvariable=format_var, values=["ODI", "T20", "Test"]).grid(
    row=len(perf_fields)+1, column=2, padx=10, pady=10)

ttk.Button(performance_frame, text="Add Performance", bootstyle="info", command=add_match_performance).grid(
    row=len(perf_fields)+2, column=1, columnspan=2, pady=20)

view_tab = ttk.Frame(notebook)
notebook.add(view_tab, text="View Players")

# === Search and Table Frame ===
view_frame = ttk.Frame(view_tab, padding=20)
view_frame.pack(fill="both", expand=True)

search_var = tk.StringVar()

def fetch_players(search_term=""):
    for row in player_table.get_children():
        player_table.delete(row)
    
    if search_term:
        query = """
            SELECT name, role, age, country, team_name, bowling_role FROM players
            WHERE name LIKE %s OR country LIKE %s OR team_name LIKE %s
        """
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
    else:
        cursor.execute("SELECT name, role, age, country, team_name, bowling_role FROM players")
    
    for row in cursor.fetchall():
        player_table.insert("", "end", values=row)

def search_players():
    fetch_players(search_var.get())

# === Search Entry and Button ===
search_frame = ttk.Frame(view_frame)
search_frame.pack(fill="x", pady=10)

# === Filter Options ===
filter_frame = ttk.LabelFrame(search_frame, text="Search/Filter", padding=10)
filter_frame.pack(fill="x", padx=10, pady=10)

search_name_var = tk.StringVar()
search_team_var = tk.StringVar()
search_country_var = tk.StringVar()

ttk.Label(filter_frame, text="Name").grid(row=0, column=0, padx=5, pady=5)
ttk.Entry(filter_frame, textvariable=search_name_var).grid(row=0, column=1, padx=5, pady=5)

ttk.Label(filter_frame, text="Team").grid(row=0, column=2, padx=5, pady=5)
ttk.Entry(filter_frame, textvariable=search_team_var).grid(row=0, column=3, padx=5, pady=5)

ttk.Label(filter_frame, text="Country").grid(row=0, column=4, padx=5, pady=5)
ttk.Entry(filter_frame, textvariable=search_country_var).grid(row=0, column=5, padx=5, pady=5)

def apply_filters():
    query = "SELECT name, role, age, country, team_name, bowling_role FROM players WHERE 1=1"
    params = []

    if search_name_var.get():
        query += " AND name LIKE %s"
        params.append(f"%{search_name_var.get()}%")
    if search_team_var.get():
        query += " AND team_name LIKE %s"
        params.append(f"%{search_team_var.get()}%")
    if search_country_var.get():
        query += " AND country LIKE %s"
        params.append(f"%{search_country_var.get()}%")

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    for i in player_tree.get_children():
        player_tree.delete(i)
    for row in rows:
        player_tree.insert("", "end", values=row)

ttk.Button(filter_frame, text="Apply Filters", bootstyle="primary", command=apply_filters).grid(
    row=0, column=6, padx=5, pady=5)

ttk.Button(filter_frame, text="Clear Filters", bootstyle="secondary", command=lambda: [
    search_name_var.set(""), search_team_var.set(""), search_country_var.set(""), load_players()
]).grid(row=0, column=7, padx=5, pady=5)


ttk.Entry(search_frame, textvariable=search_var, width=40).pack(side="left", padx=10)
ttk.Button(search_frame, text="Search", command=search_players, bootstyle="primary").pack(side="left")

# === Table ===
columns = ("Name", "Role", "Age", "Country", "Team", "Bowling Role")
player_table = ttk.Treeview(view_frame, columns=columns, show="headings", height=20)
for col in columns:
    player_table.heading(col, text=col)
    player_table.column(col, anchor="center")

player_table.pack(fill="both", expand=True, pady=10)

# === Image Preview ===
image_preview_frame = ttk.Frame(view_frame)
image_preview_frame.pack(pady=10)

player_photo_label = ttk.Label(image_preview_frame)
player_photo_label.pack(side="left", padx=20)

team_logo_label = ttk.Label(image_preview_frame)
team_logo_label.pack(side="left", padx=20)


def show_selected_images(event):
    selected_item = player_table.focus()
    if not selected_item:
        return

    selected_values = player_table.item(selected_item)["values"]
    if not selected_values:
        return

    player_name = selected_values[0]
    cursor.execute("SELECT player_photo_path, team_logo_path FROM players WHERE name = %s", (player_name,))
    result = cursor.fetchone()
    if result:
        player_photo_path, team_logo_path = result

        try:
            if player_photo_path:
                img = Image.open(player_photo_path).resize((120, 120))
                img = ImageTk.PhotoImage(img)
                player_photo_label.config(image=img)
                player_photo_label.image = img
            else:
                player_photo_label.config(image="")
        except:
            player_photo_label.config(image="")

        try:
            if team_logo_path:
                logo = Image.open(team_logo_path).resize((120, 120))
                logo = ImageTk.PhotoImage(logo)
                team_logo_label.config(image=logo)
                team_logo_label.image = logo
            else:
                team_logo_label.config(image="")
        except:
            team_logo_label.config(image="")


player_table.bind("<<TreeviewSelect>>", show_selected_images)


# === Load players initially ===
fetch_players()

# ========== Rankings Tab ==========
ranking_tab = ttk.Frame(notebook)
notebook.add(ranking_tab, text="Rankings")

ranking_notebook = ttk.Notebook(ranking_tab)
ranking_notebook.pack(fill="both", expand=True)

# ------------- Function to build each format tab (T20, ODI, Test) -------------
def build_format_tab(format_name):
    tab = ttk.Frame(ranking_notebook)
    ranking_notebook.add(tab, text=format_name)

    sub_notebook = ttk.Notebook(tab)
    sub_notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Batting Tab
    bat_tab = ttk.Frame(sub_notebook)
    sub_notebook.add(bat_tab, text="Batting")

    bat_table = ttk.Treeview(bat_tab, columns=("Player", "Matches", "Runs", "Avg"), show="headings")
    for col in bat_table["columns"]:
        bat_table.heading(col, text=col)
        bat_table.column(col, anchor="center")
    bat_table.pack(fill="both", expand=True)

    # Bowling Tab
    bowl_tab = ttk.Frame(sub_notebook)
    sub_notebook.add(bowl_tab, text="Bowling")

    bowl_table = ttk.Treeview(bowl_tab, columns=("Player", "Matches", "Wickets", "Avg"), show="headings")
    for col in bowl_table["columns"]:
        bowl_table.heading(col, text=col)
        bowl_table.column(col, anchor="center")
    bowl_table.pack(fill="both", expand=True)

    return bat_table, bowl_table

# Build all three format tabs
t20_bat_table, t20_bowl_table = build_format_tab("T20")
odi_bat_table, odi_bowl_table = build_format_tab("ODI")
test_bat_table, test_bowl_table = build_format_tab("Test")

def refresh_rankings(format, bat_table, bowl_table):
    # Batting Rankings
    bat_table.delete(*bat_table.get_children())
    cursor.execute(f"""
        SELECT p.name, COUNT(m.match_id), SUM(m.runs_scored),
               ROUND(AVG(m.runs_scored), 2)
        FROM players p
        JOIN matches m ON p.player_id = m.player_id
        WHERE m.match_format = %s
        GROUP BY p.name
        ORDER BY SUM(m.runs_scored) DESC
    """, (format,))
    for row in cursor.fetchall():
        bat_table.insert("", "end", values=row)

    # Bowling Rankings
    bowl_table.delete(*bowl_table.get_children())
    cursor.execute(f"""
        SELECT p.name, COUNT(m.match_id), SUM(m.wickets_taken),
               ROUND(SUM(m.balls_bowled)/NULLIF(SUM(m.wickets_taken), 0), 2)
        FROM players p
        JOIN matches m ON p.player_id = m.player_id
        WHERE m.match_format = %s
        GROUP BY p.name
        ORDER BY SUM(m.wickets_taken) DESC
    """, (format,))
    for row in cursor.fetchall():
        bowl_table.insert("", "end", values=row)


def on_tab_change(event):
    current_tab = notebook.tab(notebook.index("current"))["text"]
    if current_tab == "Rankings":
        refresh_rankings("T20", t20_bat_table, t20_bowl_table)
        refresh_rankings("ODI", odi_bat_table, odi_bowl_table)
        refresh_rankings("Test", test_bat_table, test_bowl_table)

notebook.bind("<<NotebookTabChanged>>", on_tab_change)



# === Initialize Dropdown ===
update_player_names()

# === Start App ===
root.mainloop()