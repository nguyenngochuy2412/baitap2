import psycopg2
from psycopg2 import extras, sql
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

def check_existed_data(connection):
    cur = connection.cursor()
    
    cur.execute('SELECT * FROM users')
    existing_users = cur.fetchall()

    # Nếu người dùng chưa tồn tại, thêm mới
    if len(existing_users) < 1:
        cur.execute('''
            INSERT INTO users (user_name, user_password, user_role) 
            VALUES 
                ('admin', '1', '1'),
                ('nva', '1', '0')
        ''')
        connection.commit()  # Xác nhận thay đổi

def create_table(connection):
    try:
        cur = connection.cursor()
        
        # Tạo bảng nếu chưa tồn tại
        cur.execute(''' 
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                user_name VARCHAR(255),
                user_password VARCHAR(255),
                user_role VARCHAR(50)
            )
        ''')
        
        # Chèn dữ liệu nếu chưa tồn tại (sử dụng ON CONFLICT)
        if check_existed_data(connection):
            cur.execute('''
                INSERT INTO users (user_name, user_password, user_role) 
                VALUES 
                    ('admin', '1', '1'),
                    ('nva', '1', '0')
            ''')

            # Xác nhận thay đổi
            connection.commit()

    except (Exception, psycopg2.Error) as error:
        messagebox.showerror(f"Error: {error}")
    
    finally:
        cur.close()  # Đóng cursor sau khi sử dụng

def connect_to_db():
    try:
        host = entry_host.get()
        database = entry_database.get()
        user = entry_user.get()
        password = entry_password.get()
        port = entry_port.get()

        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            options='-c client_encoding=UTF8'  # Cài đặt mã hóa UTF-8 cho kết nối
        )

        # Tạo bảng sau khi kết nối thành công
        create_table(connection)

        # Hiển thị trang admin
        show_admin_page(connection)
        return connection

    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Lỗi kết nối", f"Không thể kết nối: {error}")
        return None


# Hàm đăng xuất
def logout():
    if messagebox.askyesno("Đăng xuất", "Bạn có muốn đăng xuất không?"):
        for widget in win.winfo_children():
            widget.destroy()
        create_login_page()

# Hàm tạo lại trang đăng nhập
def create_login_page():
    global login_frame, entry_host, entry_database, entry_user, entry_password, entry_port
    login_frame = tk.Frame(win, padx=10, pady=10)
    login_frame.pack(padx=10, pady=10)

    # Host
    host_label = tk.Label(login_frame, text="Host:")
    host_label.grid(row=0, column=0, padx=5, pady=5)
    entry_host = tk.Entry(login_frame)
    entry_host.grid(row=0, column=1, padx=5, pady=5)
    entry_host.insert(0, "localhost")  # Giá trị mặc định cho Host

    # Database
    database_label = tk.Label(login_frame, text="Database:")
    database_label.grid(row=1, column=0, padx=5, pady=5)
    entry_database = tk.Entry(login_frame)
    entry_database.grid(row=1, column=1, padx=5, pady=5)

    # Username
    user_name_label = tk.Label(login_frame, text="Username:")
    user_name_label.grid(row=2, column=0, padx=5, pady=5)
    entry_user = tk.Entry(login_frame)
    entry_user.grid(row=2, column=1, padx=5, pady=5)
    entry_user.insert(0, "postgres")  # Giá trị mặc định cho Username

    # Password
    password_label = tk.Label(login_frame, text="Password:")
    password_label.grid(row=3, column=0, padx=5, pady=5)
    entry_password = tk.Entry(login_frame, show="*")
    entry_password.grid(row=3, column=1, padx=5, pady=5)

    # Port
    port_label = tk.Label(login_frame, text="Port:")
    port_label.grid(row=4, column=0, padx=5, pady=5)
    entry_port = tk.Entry(login_frame)
    entry_port.grid(row=4, column=1, padx=5, pady=5)
    entry_port.insert(0, "5432")  # Giá trị mặc định cho Port

    # Login Button
    login_button = tk.Button(login_frame, text="Đăng nhập", command=connect_to_db)
    login_button.grid(row=5, column=0, columnspan=2, pady=10)



def reload_table(table_name):
    if current_connection:
        with current_connection.cursor() as cur:
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()

            # Xóa dữ liệu cũ trên TreeView
            for row in list.get_children():
                list.delete(row)

            # Hiển thị dữ liệu mới
            for row in rows:
                list.insert('', 'end', values=row)

def show_table(frame, table_name):
    global list
    columns = get_column_names(table_name)
    list = ttk.Treeview(frame, columns=columns, show='headings')

    for col in columns:
        list.heading(col, text=col)
        list.column(col, width=150)

    list.pack()
    reload_table(table_name)

def get_tables(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';""")
            return cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Lỗi", f"Không thể lấy danh sách bảng: {error}")
        return []

def get_column_names(table_name):
    try:
        with current_connection.cursor() as cursor:
            query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = 'public';
            """
            cursor.execute(query, (table_name,))
            return [col[0] for col in cursor.fetchall()]
    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Lỗi", f"Không thể lấy tên cột: {error}")
        return []

def add_user():
    username = input_name.get()
    password = input_password.get()
    role = input_role.get()

    if username and password and role:
        try:
            with current_connection.cursor() as cursor:
                query = "INSERT INTO users (user_name, user_password, user_role) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, password, role))
                current_connection.commit()  # Commit if successful
                messagebox.showinfo("Thành công", "Thêm người dùng thành công!")
                reload_table('users')
        except (Exception, psycopg2.Error) as error:
            current_connection.rollback()  # Rollback on error
            messagebox.showerror("Lỗi", f"Không thể thêm người dùng: {error}")
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")

def delete_user():
    selected_item = list.selection()
    if selected_item:
        user_data = list.item(selected_item)
        username = user_data['values'][0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa người dùng '{username}' không?"):
            try:
                with current_connection.cursor() as cursor:
                    query = "DELETE FROM users WHERE user_id = %s"
                    cursor.execute(query, (username,))
                    current_connection.commit()  # Commit if successful
                    messagebox.showinfo("Thành công", "Xóa người dùng thành công!")
                    reload_table('users')
            except (Exception, psycopg2.Error) as error:
                current_connection.rollback()  # Rollback on error
                messagebox.showerror("Lỗi", f"Không thể xóa người dùng: {error}")
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng để xóa.")

def update_user():
    selected_item = list.selection()
    if selected_item:
        user_data = list.item(selected_item)
        user_name = user_data['values'][0]

        try:
            with current_connection.cursor() as cursor:
                new_username = input_name.get()
                new_password = input_password.get()
                new_role = input_role.get()

                query = "UPDATE users SET user_name = %s, user_password = %s, user_role = %s WHERE user_id = %s"
                cursor.execute(query, (new_username, new_password, new_role, user_name))
                current_connection.commit()  # Commit if successful
                messagebox.showinfo("Thành công", "Cập nhật thông tin người dùng thành công!")
                reload_table('users')
        except (Exception, psycopg2.Error) as error:
            current_connection.rollback()  # Rollback on error
            messagebox.showerror("Lỗi", f"Không thể cập nhật người dùng: {error}")
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng để cập nhật.")

# Hàm hiển thị trang quản trị

def show_admin_page(connection):

    global current_connection 
    current_connection = connection 

    login_frame.pack_forget()
    admin_frame = tk.Frame(win, padx=10, pady=10)
    admin_frame.pack()

    welcome_label = tk.Label(admin_frame, text=f"Chào mừng đến với trang quản trị!", font=("Arial", 14))
    welcome_label.pack(pady=20)

    insert_data_frame = tk.Frame(admin_frame)
    insert_data_frame.pack(pady=10)

    # Các trường nhập liệu xếp ngang
    tk.Label(insert_data_frame, text="User Name:", anchor="e", width=15).grid(row=0, column=0, padx=5, pady=5)
    global input_name
    input_name = tk.Entry(insert_data_frame)
    input_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(insert_data_frame, text="User Password:", anchor="e", width=15).grid(row=0, column=2, padx=5, pady=5)
    global input_password
    input_password = tk.Entry(insert_data_frame)
    input_password.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(insert_data_frame, text="User Role:", anchor="e", width=15).grid(row=0, column=4, padx=5, pady=5)
    global input_role
    input_role = tk.Entry(insert_data_frame)
    input_role.grid(row=0, column=5, padx=5, pady=5)
    input_role.insert(0, "0")

    # Các nút xếp ngang
    button_frame = tk.Frame(admin_frame)
    button_frame.pack(pady=10)

    btn_add = tk.Button(button_frame, text="Thêm người dùng", command=add_user)
    btn_add.grid(row=0, column=0, padx=5, pady=5)

    btn_update = tk.Button(button_frame, text="Cập nhật thông tin", command=update_user)
    btn_update.grid(row=0, column=1, padx=5, pady=5)

    btn_delete = tk.Button(button_frame, text="Xóa người dùng", command=delete_user)
    btn_delete.grid(row=0, column=2, padx=5, pady=5)

    btn_reload = tk.Button(button_frame, text="Tải lại bảng", command=lambda: reload_table('users'))
    btn_reload.grid(row=0, column=3, padx=5, pady=5)

    # Lấy và hiển thị bảng từ cơ sở dữ liệu
    tables = get_tables(current_connection)

    tables_label = tk.Label(admin_frame, text="Danh sách  bảng và nội dung trong csdl:", font=("Arial", 12))
    tables_label.pack(pady=10)

    for table in tables:
        table_name = table[0]
        table_label = tk.Label(admin_frame, text=f"Bảng: {table_name}", font=("Arial", 10, "bold"))
        table_label.pack(pady=5)

        frame_tree = tk.Frame(admin_frame)
        frame_tree.pack(pady=5, fill="both", expand=True)

        show_table(frame_tree, table_name)

    logout_button = tk.Button(admin_frame, text="Đăng xuất", command=logout)
    logout_button.pack(pady=10)

   

# Khởi tạo cửa sổ ứng dụng
win = tk.Tk()
win.title("Hệ thống quản lý người dùng")


create_login_page()

# Chạy ứng dụngd
win.mainloop()