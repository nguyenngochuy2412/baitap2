import tkinter as tk
from tkinter import ttk
from database import Database
from functions import UserManagement
from tkinter import messagebox

class UserManagementApp:
    def __init__(self, win):
        self.win = win
        self.win.title("Hệ Thống Quản Lý Người Dùng")

        self.db = Database()  # Tạo đối tượng Database
        self.user_management = UserManagement(self.db)  # Tạo đối tượng UserManagement

        self.create_login_page()  # Gọi hàm tạo trang đăng nhập

    # Tạo trang đăng nhập
    def create_login_page(self):
        self.login_frame = tk.Frame(self.win, padx=10, pady=10)
        self.login_frame.pack(padx=10, pady=10)

        # Cấu hình các cột của grid để các ô có chiều rộng đều
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_columnconfigure(1, weight=3)

        # Nhập thông tin kết nối
        self.create_connection_inputs()

        # Nút Đăng nhập
        login_button = tk.Button(self.login_frame, text="Đăng nhập", command=self.connect_to_db)
        login_button.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

    # Nhập thông tin kết nối
    def create_connection_inputs(self):
        # Host
        tk.Label(self.login_frame, text="Host:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_host = tk.Entry(self.login_frame)
        self.entry_host.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.entry_host.insert(0, "localhost")  # Giá trị mặc định cho Host

        # Database
        tk.Label(self.login_frame, text="Database:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_database = tk.Entry(self.login_frame)
        self.entry_database.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Username
        tk.Label(self.login_frame, text="Username:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_user = tk.Entry(self.login_frame)
        self.entry_user.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.entry_user.insert(0, "postgres")  # Giá trị mặc định cho Username

        # Password
        tk.Label(self.login_frame, text="Password:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.entry_password = tk.Entry(self.login_frame, show="*")
        self.entry_password.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Port
        tk.Label(self.login_frame, text="Port:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.entry_port = tk.Entry(self.login_frame)
        self.entry_port.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.entry_port.insert(0, "5432")  # Giá trị mặc định cho Port

    # Kết nối đến cơ sở dữ liệu và hiển thị trang admin
    def connect_to_db(self):
        host = self.entry_host.get()
        database = self.entry_database.get()
        user = self.entry_user.get()
        password = self.entry_password.get()
        port = self.entry_port.get()

        connection = self.db.connect(host, database, user, password, port)
        if connection:
            self.show_admin_page()  # Gọi hàm hiển thị trang quản trị nếu kết nối thành công
        else:
            messagebox.showerror("Lỗi kết nối", "Không thể kết nối đến cơ sở dữ liệu.")  # Thông báo lỗi

    # Hiển thị trang quản trị
    def show_admin_page(self):
        self.login_frame.pack_forget()  # Ẩn khung đăng nhập
        admin_frame = tk.Frame(self.win, padx=10, pady=10)
        admin_frame.pack()

        tk.Label(admin_frame, text=f"Chào Mừng Đến Trang Quản Trị!", font=("Arial", 16)).pack(pady=10)

        # Tạo khung nhập liệu cho người dùng mới
        self.create_user_input_frame(admin_frame)

        # TreeView cho người dùng
        self.list_widget = ttk.Treeview(admin_frame, columns=('ID', 'Tên', 'Mật khẩu', 'Vai trò'), show='headings')
        self.list_widget.heading('ID', text='ID')  # Đặt tiêu đề cho cột ID
        self.list_widget.heading('Tên', text='Tên')  # Đặt tiêu đề cho cột Tên
        self.list_widget.heading('Mật khẩu', text='Mật khẩu')  # Đặt tiêu đề cho cột Mật khẩu
        self.list_widget.heading('Vai trò', text='Vai trò')  # Đặt tiêu đề cho cột Vai trò
        self.list_widget.pack()

        # Tải lại dữ liệu
        self.user_management.reload_table('users', self.list_widget)  # Tải lại bảng người dùng

    # Tạo khung nhập liệu cho người dùng mới
    def create_user_input_frame(self, parent):
        input_frame = tk.Frame(parent)
        input_frame.pack(pady=10)

        # Cấu hình các cột của grid để các ô nhập liệu và nút có chiều rộng đều
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=3)

        # Nhập tên người dùng
        tk.Label(input_frame, text="Tên người dùng:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_username = tk.Entry(input_frame)
        self.entry_username.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Nhập mật khẩu
        tk.Label(input_frame, text="Mật khẩu:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_password_new = tk.Entry(input_frame, show="*")
        self.entry_password_new.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Nhập vai trò
        tk.Label(input_frame, text="Vai trò:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_role = tk.Entry(input_frame)
        self.entry_role.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        # Tạo một Frame chứa các nút hành động nằm ngang
        action_frame = tk.Frame(input_frame)
        action_frame.grid(row=1, column=0, columnspan=6, pady=5, sticky="ew")

        # Nút Thêm người dùng
        add_button = tk.Button(action_frame, text="Thêm người dùng", command=self.add_user)
        add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Nút Xóa người dùng
        delete_button = tk.Button(action_frame, text="Xóa người dùng", command=self.delete_user)
        delete_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Nút Cập nhật người dùng
        update_button = tk.Button(action_frame, text="Cập nhật người dùng", command=self.update_user)
        update_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    # Thêm người dùng mới
    def add_user(self):
        username = self.entry_username.get()  # Lấy tên người dùng từ ô nhập
        password = self.entry_password_new.get()  # Lấy mật khẩu từ ô nhập
        role = self.entry_role.get()  # Lấy vai trò từ ô nhập
        self.user_management.add_user(username, password, role, self.list_widget)  # Gọi hàm thêm người dùng

    # Xóa người dùng đã chọn
    def delete_user(self):
        selected_item = self.list_widget.selection()  # Lấy mục đã chọn
        if selected_item:
            self.user_management.delete_user(selected_item[0], self.list_widget)  # Gọi hàm xóa người dùng

    # Cập nhật thông tin người dùng
    def update_user(self):
        selected_item = self.list_widget.selection()  # Lấy mục đã chọn
        if selected_item:
            self.user_management.update_user(selected_item[0], self.entry_username.get(), self.entry_password_new.get(), self.entry_role.get(), self.list_widget)  # Cập nhật người dùng

if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagementApp(root)
    root.mainloop()
