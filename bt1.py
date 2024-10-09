import tkinter as tk
from tkinter import messagebox

class QuanLyTieuThuNuoc:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Tiêu Thụ Nước")
        
        # Ngưỡng cảnh báo cho lượng nước tiêu thụ (m3)
        self.nguong_nuoc = 30  # Ví dụ: 30 m3 là ngưỡng
        self.gia_nuoc = 7000   # Giá tiền mỗi m3 nước
        self.recent_nuoc = 0   # Lượng nước gần nhất nhập vào
        
        # Thiết lập giao diện
        self.giao_dien()

    def giao_dien(self):
        # Label và Entry cho lượng nước tiêu thụ
        self.label_nuoc = tk.Label(self.root, text="Nhập lượng nước tiêu thụ (m3):")
        self.label_nuoc.pack(pady=10)
        self.entry_nuoc = tk.Entry(self.root)
        self.entry_nuoc.pack(pady=5)
        
        # Nút kiểm tra tiêu thụ
        self.button_kiemtra = tk.Button(self.root, text="Kiểm tra", command=self.nhap_data)
        self.button_kiemtra.pack(pady=10)
        
        # Nút hiển thị tổng chi phí
        self.button_tinhchiphi = tk.Button(self.root, text="Hiển thị tổng chi phí", command=self.tinh_toan_chiphi)
        self.button_tinhchiphi.pack(pady=10)
        
        # Nút hiển thị thông số gần nhất
        self.button_thongso = tk.Button(self.root, text="Xem thông số gần đây", command=self.hien_thi_thong_so)
        self.button_thongso.pack(pady=10)

    def nhap_data(self):
        try:
            # Lấy giá trị từ Entry
            nuoc = float(self.entry_nuoc.get())
            self.recent_nuoc = nuoc
            
            # Kiểm tra nếu vượt ngưỡng
            if nuoc > self.nguong_nuoc:
                messagebox.showwarning("Cảnh báo", f"Lượng nước tiêu thụ {nuoc} m3 đã vượt ngưỡng {self.nguong_nuoc} m3!")
            else:
                messagebox.showinfo("Thông báo", "Lượng nước tiêu thụ trong ngưỡng cho phép.")
            
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập một số hợp lệ.")

    def tinh_toan_chiphi(self):
        # Tính toán chi phí dựa trên lượng nước tiêu thụ
        chi_phi = self.recent_nuoc * self.gia_nuoc
        messagebox.showinfo("Tổng chi phí", f"Tổng chi phí cho lượng nước tiêu thụ {self.recent_nuoc} m3 là {chi_phi} VND.")
    
    def hien_thi_thong_so(self):
        # Hiển thị thông số nước tiêu thụ gần nhất
        messagebox.showinfo("Thông số gần nhất", f"Lượng nước tiêu thụ gần đây: {self.recent_nuoc} m3.")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = QuanLyTieuThuNuoc(root)
    root.mainloop()
