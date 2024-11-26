import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
import psycopg2


class QuanLySach:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý thông tin sách")
        self.root.geometry("800x600")

        # Tạo Frame riêng cho nội dung của ứng dụng
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True)

        # Thông tin mặc định để kết nối PostgreSQL
        self.db_name = 'QuanLySach'
        self.user = 'postgres'
        self.password = '2111'
        self.host = 'localhost'
        self.port = '5432'

        # Tạo thanh menu
        self.create_menu()

        # Danh sách để lưu trữ dữ liệu sách
        self.sach_list = []

        # Giao diện
        self.giao_dien()

        # Xử lý đóng kết nối khi thoát chương trình
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Trang chủ
        home_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Trang chủ", menu=home_menu)
        home_menu.add_command(label="Quản lý sách", command=self.giao_dien)

        # Menu Tìm kiếm
        search_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tìm kiếm sách", menu=search_menu)
        search_menu.add_command(label="Tìm kiếm sách", command=self.tim_kiem)

        # Menu Cài đặt
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cài đặt", menu=settings_menu)
        settings_menu.add_command(label="Kết nối CSDL", command=self.create_connection_form)

        # Menu Thoát
        menubar.add_command(label="Thoát", command=self.root.quit)

    def giao_dien(self):
        self.clear_content()

        # Frame nhập thông tin sách
        frame_nhap = ttk.LabelFrame(self.content_frame, text="Nhập thông tin sách", padding=(10, 5))
        frame_nhap.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_nhap, text="Tên sách:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_title = ttk.Entry(frame_nhap)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_nhap, text="Tác giả:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_author = ttk.Entry(frame_nhap)
        self.entry_author.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_nhap, text="Thể loại:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_genre = ttk.Entry(frame_nhap)
        self.entry_genre.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_nhap, text="Ngày xuất bản:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_date = DateEntry(frame_nhap, date_pattern="yyyy-mm-dd", width=18)
        self.entry_date.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_nhap, text="Số lượng:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_quantity = ttk.Entry(frame_nhap)
        self.entry_quantity.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(frame_nhap, text="Thêm sách", command=self.them_sach).grid(row=5, column=0, columnspan=2, pady=10)

        # Frame hiển thị danh sách sách
        frame_ds = ttk.LabelFrame(self.content_frame, text="Danh sách sách", padding=(10, 5))
        frame_ds.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(frame_ds, columns=("title", "author", "genre", "date", "quantity"), show="headings")
        self.tree.heading("title", text="Tên sách")
        self.tree.heading("author", text="Tác giả")
        self.tree.heading("genre", text="Thể loại")
        self.tree.heading("date", text="Ngày xuất bản")
        self.tree.heading("quantity", text="Số lượng")
        self.tree.column("quantity", width=80)  # Đặt chiều rộng cho cột "Số lượng"
        self.tree.pack(fill="both", expand=True)

        # Frame chức năng
        frame_chucnang = ttk.Frame(self.content_frame)
        frame_chucnang.pack(padx=10, pady=10, fill="x")

        ttk.Button(frame_chucnang, text="Xóa sách", command=self.xoa_sach).pack(side="left", padx=5)
        ttk.Button(frame_chucnang, text="Hiển thị tất cả", command=self.hien_thi_tat_ca).pack(side="left", padx=5)

    def them_sach(self):
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        genre = self.entry_genre.get().strip()
        date = self.entry_date.get()  # Lấy ngày từ DateEntry
        quantity = self.entry_quantity.get().strip()

        # Kiểm tra dữ liệu nhập
        if not title or not author or not genre or not date or not quantity:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            quantity = int(quantity)  # Kiểm tra số lượng là số nguyên
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên!")
            return

        try:
            # Ghi dữ liệu vào cơ sở dữ liệu PostgreSQL
            query = """
            INSERT INTO books (title, author, genre, publish_date, quantity)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (title, author, genre, date, quantity))
            self.conn.commit()

            messagebox.showinfo("Thành công", "Thêm sách thành công!")
            self.hien_thi_tat_ca()  # Hiển thị lại danh sách
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm sách: {e}")

    def hien_thi_tat_ca(self):
        # Xóa dữ liệu hiện tại trên Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            # Lấy dữ liệu từ cơ sở dữ liệu PostgreSQL
            query = "SELECT title, author, genre, publish_date, quantity FROM books"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            # Hiển thị dữ liệu trong Treeview
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị dữ liệu: {e}")

    def xoa_sach(self):
        # Lấy dòng đang chọn
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sách cần xóa!")
            return

        try:
            for item in selected_item:
                values = self.tree.item(item, "values")
                title = values[0]
                author = values[1]

                # Xóa sách khỏi cơ sở dữ liệu
                query = "DELETE FROM books WHERE title = %s AND author = %s"
                self.cursor.execute(query, (title, author))
                self.conn.commit()

                # Xóa sách khỏi giao diện
                self.tree.delete(item)

            messagebox.showinfo("Thành công", "Xóa sách thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa sách: {e}")

    def tim_kiem(self):
        keyword = simpledialog.askstring("Tìm kiếm", "Nhập từ khóa để tìm kiếm:")
        if not keyword:
            return

        try:
            # Lọc sách theo từ khóa trong cơ sở dữ liệu
            query = """
            SELECT title, author, genre, publish_date, quantity 
            FROM books 
            WHERE title ILIKE %s OR author ILIKE %s OR genre ILIKE %s
            """
            self.cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            rows = self.cursor.fetchall()

            # Xóa dữ liệu hiện tại trên Treeview
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Hiển thị kết quả tìm kiếm
            for row in rows:
                self.tree.insert("", tk.END, values=row)

            if not rows:
                messagebox.showinfo("Kết quả", "Không tìm thấy sách nào phù hợp!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tìm kiếm sách: {e}")

    def create_connection_form(self):
        self.clear_content()

        tk.Label(self.content_frame, text="DB Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.db_name_entry = tk.Entry(self.content_frame)
        self.db_name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.content_frame, text="User:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.user_entry = tk.Entry(self.content_frame)
        self.user_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.content_frame, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = tk.Entry(self.content_frame, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.content_frame, text="Host:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.host_entry = tk.Entry(self.content_frame)
        self.host_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self.content_frame, text="Port:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.port_entry = tk.Entry(self.content_frame)
        self.port_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self.content_frame, text="Table Name:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.table_name_entry = tk.Entry(self.content_frame)
        self.table_name_entry.grid(row=5, column=1, padx=10, pady=5)

        self.connect_button = tk.Button(self.content_frame, text="Connect", command=self.connect_to_db)
        self.connect_button.grid(row=6, column=1, padx=10, pady=10)

        self.load_button = tk.Button(self.content_frame, text="Load Data", command=self.load_data)
        self.load_button.grid(row=7, column=1, padx=10, pady=10)

        self.status_label = tk.Label(self.content_frame, text="Not connected", fg="red")
        self.status_label.grid(row=8, column=1, padx=10, pady=5)

        # Khung trắng để hiển thị dữ liệu
        self.data_display = tk.Text(self.content_frame, height=10, width=70)
        self.data_display.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    def connect_to_db(self):
        db_name = self.db_name_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        host = self.host_entry.get()
        port = self.port_entry.get()

        if not all([db_name, user, password, host, port]):
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin kết nối!")
            return

        try:
            self.conn = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.cursor = self.conn.cursor()
            self.status_label.config(text="Connected", fg="green")
            messagebox.showinfo("Thành công", "Kết nối thành công!")
        except Exception as e:
            self.status_label.config(text="Not connected", fg="red")
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến cơ sở dữ liệu: {e}")

    def load_data(self):
        try:
            table_name = self.table_name_entry.get()
            if not table_name:
                messagebox.showwarning("Lỗi", "Vui lòng nhập tên bảng!")
                return

            query = f"SELECT * FROM {table_name};"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            # Xóa tất cả nội dung trong khung dữ liệu trước khi load dữ liệu mới
            self.data_display.delete(1.0, tk.END)

            for row in rows:
                row_display = f"{row}\n"  # Chuyển dữ liệu thành chuỗi để hiển thị
                self.data_display.insert(tk.END, row_display)

            messagebox.showinfo("Thành công", "Dữ liệu đã được tải thành công từ cơ sở dữ liệu!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def on_close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        self.root.destroy()


# Chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()
    app = QuanLySach(root)
    root.mainloop()
