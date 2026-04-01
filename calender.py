import tkinter as tk
from tkcalendar import Calendar
from tkinter import messagebox
import json
import os
from plyer import notification
from datetime import datetime

DATA_FILE = "schedule_full_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    refresh_calendar_marks()
    update_listbox() # 一覧表示も更新

def refresh_calendar_marks():
    cal.calevent_remove('all')
    data = load_data()
    for date_str, tasks in data.items():
        if tasks:
            date_obj = cal.datetime.strptime(date_str, '%Y-%m-%d').date()
            cal.calevent_create(date_obj, 'Schedule', 'message')
    cal.tag_config('message', background='skyblue', foreground='black')

def update_listbox():
    """保存されているすべての予定を一覧に表示する"""
    listbox.delete(0, tk.END)
    data = load_data()
    # 日付順にソートして表示
    for date_str in sorted(data.keys()):
        for i, item in enumerate(data[date_str]):
            listbox.insert(tk.END, f"{date_str} {item['time']} - {item['task']}")

def delete_selected():
    """一覧で選択された予定を削除する"""
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("警告", "削除する予定を選択してください")
        return
    
    # 選択されたテキストを取得
    target_text = listbox.get(selected[0])
    # テキストから日付、時間、内容を分解（簡易的）
    date_part = target_text.split(" ")[0]
    time_part = target_text.split(" ")[1]
    
    data = load_data()
    if date_part in data:
        # 一致する予定を除外
        data[date_part] = [item for item in data[date_part] if not (item['time'] == time_part)]
        if not data[date_part]:
            del data[date_part]
        save_data(data)
        messagebox.showinfo("削除", "予定を削除しました")

def save_schedule():
    selected_date = cal.get_date()
    time_val = entry_time.get()
    task_val = entry_task.get()
    
    if not time_val or not task_val:
        messagebox.showwarning("エラー", "時間と内容を入力してください")
        return

    data = load_data()
    if selected_date not in data:
        data[selected_date] = []
    
    data[selected_date].append({"time": time_val, "task": task_val})
    # 時間順に並び替え
    data[selected_date] = sorted(data[selected_date], key=lambda x: x['time'])
    
    save_data(data)
    messagebox.showinfo("成功", "予定を追加しました")

# UI構築
root = tk.Tk()
root.title("予定一覧付きスケジュール帳")
root.geometry("450x700")

# 上部：カレンダー
cal = Calendar(root, selectmode='day', locale='ja_JP', date_pattern='yyyy-mm-dd')
cal.pack(pady=10)

# 中部：入力エリア
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="時間:").grid(row=0, column=0)
entry_time = tk.Entry(frame_input, width=8)
entry_time.insert(0, "12:00")
entry_time.grid(row=0, column=1, padx=5)

tk.Label(frame_input, text="内容:").grid(row=1, column=0)
entry_task = tk.Entry(frame_input, width=30)
entry_task.grid(row=1, column=1, padx=5, pady=5)

btn_save = tk.Button(root, text="予定を追加", command=save_schedule, bg="#4CAF50", fg="white")
btn_save.pack()

# 下部：一覧表示エリア
tk.Label(root, text="--- 予定一覧 ---").pack(pady=(20, 0))
frame_list = tk.Frame(root)
frame_list.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(frame_list, width=50, height=10, yscrollcommand=scrollbar.set)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox.yview)

btn_delete = tk.Button(root, text="選択した予定を削除", command=delete_selected, bg="#f44336", fg="white")
btn_delete.pack(pady=10)

# 初期化
refresh_calendar_marks()
update_listbox()

root.mainloop()
