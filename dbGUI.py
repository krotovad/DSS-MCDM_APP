import sqlite3
import PySimpleGUI as sg
from screeninfo import get_monitors

def draw_table(graph, name, columns, x, y, max_text_len):
    text_center = x + max_text_len // 2
    graph.draw_rectangle((x, y), (x + max_text_len, y - 20 * len(columns) - 20), line_color='black', fill_color='lightgray')
    graph.draw_text(name, (text_center, y - 10), text_location=sg.TEXT_LOCATION_CENTER)

    for i, col in enumerate(columns):
        graph.draw_text(col, (text_center, y - 30 - i * 20), text_location=sg.TEXT_LOCATION_CENTER)

def get_tables_and_columns():
    conn = sqlite3.connect("agricultural_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    table_column_dict = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        table_column_dict[table_name] = column_names

    return table_column_dict

def main():
    table_column_dict = get_tables_and_columns()
    num_tables = len(table_column_dict)

    # Auto-detect screen width
    screen_width = get_monitors()[0].width

    # Calculate required canvas size
    margin = 50
    max_text_len = max([max([len(col) for col in cols]) for cols in table_column_dict.values()]) * 8 + 20
    tables_per_row = screen_width // (max_text_len + margin)
    num_rows = -(-num_tables // tables_per_row)  # Ceiling division
    canvas_height = num_rows * 220  # 200 = estimated max height of a table block + 20 as a margin

    layout = [
        [sg.Graph(canvas_size=(screen_width, canvas_height), graph_bottom_left=(0, -canvas_height), graph_top_right=(screen_width, 0), background_color='white', key='graph', enable_events=True)],
        [sg.Text("Table Relations:"), sg.Multiline("", size=(80, 10), key="-RELATIONS-", background_color='#D3D3D3')]  # Custom background color
    ]

    window = sg.Window("Database Logical Model", layout, finalize=True)
    graph = window['graph']
    
    x, y = margin, -margin
    for table, columns in table_column_dict.items():
        draw_table(graph, table, columns, x, y, max_text_len)
        x += max_text_len + margin

        # Move to the next row if we exceed screen width
        if x + max_text_len + margin > screen_width:
            x = margin
            y -= 220  # 200 = estimated max height of table block + 20 as a margin

    # Your logic to get relations from the SQLite DB
    relations = [("Farm", "Equipment"), ("Farm", "Employee")]  # Example, replace with your actual relations
    relation_text = ", ".join([f"{rel[0]} -> {rel[1]}" for rel in relations])
    window["-RELATIONS-"].update(relation_text)

    window.read(close=True)

if __name__ == "__main__":
    main()
