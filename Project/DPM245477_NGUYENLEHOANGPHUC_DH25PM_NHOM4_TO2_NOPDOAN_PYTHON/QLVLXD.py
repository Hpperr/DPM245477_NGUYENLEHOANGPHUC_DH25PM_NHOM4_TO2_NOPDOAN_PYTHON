import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db_manager import DBManager
import uuid 

class StoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quản Lý Vật Liệu Xây Dựng")
        self.geometry("1200x750")
        self.db_manager = DBManager(
            server='DESKTOP-9FLA8Q5\\SQLEXPRESS',
            database='model',        
            username='sa',                          
            password='sql2025'                
        )
        tk.Label(self, text="Quản Lý Vật Liệu Xây Dựng", 
             font=("Arial", 18, "bold"), 
             bg="#4d6f8f", fg="white").pack(fill="x", pady=5)
    
        # Tạo Tab
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tab 1: Quản lý Vật Tư
        self.tab_material = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_material, text="Quản lý Vật Tư")
        
        # Tab 2: Quản lý Nhân Viên
        self.tab_employee = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_employee, text="Quản lý Nhân Viên")
        
        # Tab 3: Chi tiết Hóa đơn
        self.tab_invoice_detail = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_invoice_detail, text="Chi tiết Hóa đơn")
        
        self.create_material_view()
        self.create_employee_view()
        self.create_invoice_detail_view()
        self.load_material_data()
        self.load_employee_data()
        self.load_invoice_detail_data()

    def _clean_row(self, row, expected_len=None):
        """Chuyển một row (pyodbc.Row, tuple, hoặc chuỗi) thành tuple các chuỗi sạch.
        Loại bỏ ngoặc và dấu nháy, thay None bằng chuỗi rỗng.
        """
        if row is None:
            if expected_len:
                return tuple('' for _ in range(expected_len))
            return ('',)
        # Nếu là iterable (tuple/pyodbc.Row) và không phải chuỗi
        try:
            if hasattr(row, '__iter__') and not isinstance(row, (str, bytes)):
                vals = []
                for v in row:
                    if v is None:
                        vals.append('')
                    else:
                        vals.append(str(v))
                if expected_len and len(vals) < expected_len:
                    vals += [''] * (expected_len - len(vals))
                return tuple(v.replace("'", "").strip() for v in vals)
        except Exception:
            pass
        # Fallback: xử lý chuỗi dạng "('A','B',70)"
        s = str(row)
        s = s.strip()
        s = s.strip('()[]')
        # loại bỏ dấu nháy đơn
        s = s.replace("'", "")
        parts = [p.strip() for p in s.split(',')] if ',' in s else [s]
        if expected_len and len(parts) < expected_len:
            parts += [''] * (expected_len - len(parts))
        return tuple(parts)

    def load_material_data(self):
        for item in self.material_tree.get_children():
            self.material_tree.delete(item)
        data = self.db_manager.fetch_all_materials()
        for row in data:
            vals = self._clean_row(row, expected_len=4)
            # convert SoLuongTon to int when possible
            try:
                so_luong = int(vals[3]) if vals[3] != '' else 0
            except Exception:
                so_luong = vals[3]
            self.material_tree.insert("", tk.END, values=(vals[0], vals[1], vals[2], so_luong))
    
    def on_material_select(self, event):
       
        sel = self.material_tree.selection()
        if not sel:
            return
        item = self.material_tree.item(sel[0])
        vals = item.get("values", [])
        # Ensure cleaned
        if vals:
            vals = tuple(str(v).replace("'", "").strip() for v in vals)
        if not vals:
            return
        self.selected_ma_vt = str(vals[0])
        self.entry_mavt.config(state='normal')
        self.entry_mavt.delete(0, tk.END)
        self.entry_mavt.insert(0, self.selected_ma_vt)
        self.entry_mavt.config(state='readonly')
        self.entry_ten.delete(0, tk.END)
        self.entry_ten.insert(0, vals[1] if len(vals) > 1 else "")
        self.entry_dvt.delete(0, tk.END)
        self.entry_dvt.insert(0, vals[2] if len(vals) > 2 else "")
        self.entry_sl.delete(0, tk.END)
        self.entry_sl.insert(0, str(vals[3]) if len(vals) > 3 else "")
    
    def clear_material_entries(self):
        
        self.entry_mavt.config(state='normal')
        self.entry_mavt.delete(0, tk.END)
        self.entry_mavt.config(state='readonly')
        self.entry_ten.delete(0, tk.END)
        self.entry_dvt.delete(0, tk.END)
        self.entry_sl.delete(0, tk.END)

    def add_material_action(self):
    
        ten_vt = self.entry_ten.get().strip()
        don_vi = self.entry_dvt.get().strip()
        so_luong_str = self.entry_sl.get().strip()

        if not all([ten_vt, don_vi, so_luong_str]):
             messagebox.showwarning("Thiếu Thông Tin", "Vui lòng điền đủ các trường.")
             return
             
        try:
            so_luong = int(so_luong_str)
        except ValueError:
            messagebox.showerror("Lỗi Dữ Liệu", "Số Lượng phải là số nguyên.")
            return
        ma_vt = str(uuid.uuid4()).split('-')[0].upper() 
        if self.db_manager.insert_material(ma_vt, ten_vt, don_vi, so_luong):
            self.load_material_data() 
            self.clear_material_entries()
            self.selected_ma_vt = None

    def update_material_action(self):
    
        if not hasattr(self, 'selected_ma_vt') or not self.selected_ma_vt:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn vật tư từ danh sách để sửa.")
            return
        
        ten_vt = self.entry_ten.get().strip()
        don_vi = self.entry_dvt.get().strip()
        so_luong_str = self.entry_sl.get().strip()
        
        if not all([ten_vt, don_vi, so_luong_str]):
            messagebox.showwarning("Thiếu Thông Tin", "Vui lòng điền đủ các trường.")
            return
        
        try:
            so_luong = int(so_luong_str)
        except ValueError:
            messagebox.showerror("Lỗi Dữ Liệu", "Số Lượng phải là số nguyên.")
            return
        
        if self.db_manager.update_material(self.selected_ma_vt, ten_vt, don_vi, so_luong):
            self.load_material_data()
            self.clear_material_entries()
            self.selected_ma_vt = None
            messagebox.showinfo("Thành công", "Cập nhật vật tư thành công!")
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật vật tư.")

    def delete_material_action(self):
       
        if not hasattr(self, 'selected_ma_vt') or not self.selected_ma_vt:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn vật tư từ danh sách để xóa.")
            return
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn xóa vật tư '{self.selected_ma_vt}' không?"):
            if self.db_manager.delete_material(self.selected_ma_vt):
                self.load_material_data()
                self.clear_material_entries()
                self.selected_ma_vt = None
                messagebox.showinfo("Thành công", "Xóa vật tư thành công!")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa vật tư.")
    def create_material_view(self):
        
        main_frame = ttk.Frame(self.tab_material)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        frame_input = ttk.LabelFrame(main_frame, text="THÔNG TIN VẬT TƯ", padding=(10, 5))
        frame_input.pack(side="left", fill="y", padx=10, pady=10)
        input_grid = ttk.Frame(frame_input)
        input_grid.pack(padx=10, pady=10)
        ttk.Label(input_grid, text="Mã Vật Tư:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_mavt = ttk.Entry(input_grid, width=30, state='readonly') 
        self.entry_mavt.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(input_grid, text="Tên Vật Tư:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_ten = ttk.Entry(input_grid, width=30)
        self.entry_ten.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(input_grid, text="Đơn Vị Tính:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_dvt = ttk.Entry(input_grid, width=30)
        self.entry_dvt.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(input_grid, text="Số Lượng Nhập/Tồn:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_sl = ttk.Entry(input_grid, width=30)
        self.entry_sl.grid(row=3, column=1, padx=5, pady=5)
        frame_buttons = ttk.Frame(frame_input)
        frame_buttons.pack(pady=20, fill="x")
        ttk.Button(frame_buttons, text="Thêm", command=self.add_material_action).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Sửa", command=self.update_material_action).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Xóa", command=self.delete_material_action).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Hủy", command=self.clear_material_entries).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Thoát", command=self.quit).pack(side="left", padx=5)
        frame_table = ttk.LabelFrame(main_frame, text="DANH SÁCH VẬT TƯ", padding=(10, 5))
        frame_table.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        cols = ("MaVT", "TenVT", "DonVi", "SoLuongTon")
        self.material_tree = ttk.Treeview(frame_table, columns=cols, show="headings")
        self.material_tree.heading("MaVT", text="Mã VT")
        self.material_tree.heading("TenVT", text="Tên Vật Tư")
        self.material_tree.heading("DonVi", text="Đơn Vị")
        self.material_tree.heading("SoLuongTon", text="Tồn Kho")
        self.material_tree.column("MaVT", width=80, anchor=tk.CENTER)
        self.material_tree.column("TenVT", width=300)
        self.material_tree.column("DonVi", width=100)
        self.material_tree.column("SoLuongTon", width=100, anchor=tk.CENTER)
        vsb = ttk.Scrollbar(frame_table, orient="vertical", command=self.material_tree.yview)
        vsb.pack(side="right", fill="y")
        self.material_tree.configure(yscrollcommand=vsb.set)   
        self.material_tree.pack(fill="both", expand=True)
        self.material_tree.bind("<<TreeviewSelect>>", self.on_material_select)
        ttk.Button(frame_table, text="Tải lại Danh sách", command=self.load_material_data).pack(pady=5)
        self.selected_ma_vt = None

    def create_employee_view(self):
        
        main_frame = ttk.Frame(self.tab_employee)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        frame_input = ttk.LabelFrame(main_frame, text="THÔNG TIN NHÂN VIÊN", padding=(10, 5))
        frame_input.pack(side="left", fill="y", padx=10, pady=10)
        input_grid = ttk.Frame(frame_input)
        input_grid.pack(padx=10, pady=10)
        
        ttk.Label(input_grid, text="Mã NV:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_manv = ttk.Entry(input_grid, width=30)
        self.entry_manv.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_grid, text="Tên Nhân Viên:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_tennv = ttk.Entry(input_grid, width=30)
        self.entry_tennv.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_grid, text="Số Điện Thoại:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_sdt = ttk.Entry(input_grid, width=30)
        self.entry_sdt.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(input_grid, text="Địa Chỉ:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_diachi = ttk.Entry(input_grid, width=30)
        self.entry_diachi.grid(row=3, column=1, padx=5, pady=5)
        
        frame_buttons = ttk.Frame(frame_input)
        frame_buttons.pack(pady=20, fill="x")
        ttk.Button(frame_buttons, text="Thêm", command=self.add_employee_action).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Sửa", command=self.update_employee_action).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Xóa", command=self.delete_employee_action).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Hủy", command=self.clear_employee_entries).pack(side="left", padx=5)
        
        frame_table = ttk.LabelFrame(main_frame, text="DANH SÁCH NHÂN VIÊN", padding=(10, 5))
        frame_table.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        cols = ("MaNV", "TenNV", "SDT", "DiaChi")
        self.employee_tree = ttk.Treeview(frame_table, columns=cols, show="headings")
        self.employee_tree.heading("MaNV", text="Mã NV")
        self.employee_tree.heading("TenNV", text="Tên Nhân Viên")
        self.employee_tree.heading("SDT", text="Số Điện Thoại")
        self.employee_tree.heading("DiaChi", text="Địa Chỉ")
        self.employee_tree.column("MaNV", width=60, anchor=tk.CENTER)
        self.employee_tree.column("TenNV", width=200)
        self.employee_tree.column("SDT", width=120)
        self.employee_tree.column("DiaChi", width=200)
        vsb = ttk.Scrollbar(frame_table, orient="vertical", command=self.employee_tree.yview)
        vsb.pack(side="right", fill="y")
        self.employee_tree.configure(yscrollcommand=vsb.set)
        self.employee_tree.pack(fill="both", expand=True)
        self.employee_tree.bind("<<TreeviewSelect>>", self.on_employee_select)
        ttk.Button(frame_table, text="Tải lại Danh sách", command=self.load_employee_data).pack(pady=5)
        self.selected_ma_nv = None
    
    def load_employee_data(self):
       
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        data = self.db_manager.fetch_all_employees()
        for row in data:
            vals = self._clean_row(row, expected_len=4)
            self.employee_tree.insert("", tk.END, values=(vals[0], vals[1], vals[2], vals[3]))
    
    def on_employee_select(self, event):
       
        sel = self.employee_tree.selection()
        if not sel:
            return
        item = self.employee_tree.item(sel[0])
        vals = item.get("values", [])
        if vals:
            vals = tuple(str(v).replace("'", "").strip() for v in vals)
        if not vals:
            return
        self.selected_ma_nv = str(vals[0])
        self.entry_manv.delete(0, tk.END)
        self.entry_manv.insert(0, self.selected_ma_nv)
        self.entry_tennv.delete(0, tk.END)
        self.entry_tennv.insert(0, vals[1] if len(vals) > 1 else "")
        self.entry_sdt.delete(0, tk.END)
        self.entry_sdt.insert(0, vals[2] if len(vals) > 2 else "")
        self.entry_diachi.delete(0, tk.END)
        self.entry_diachi.insert(0, vals[3] if len(vals) > 3 else "")
    
    def clear_employee_entries(self):
        
        self.entry_manv.delete(0, tk.END)
        self.entry_tennv.delete(0, tk.END)
        self.entry_sdt.delete(0, tk.END)
        self.entry_diachi.delete(0, tk.END)
        self.selected_ma_nv = None
    
    def add_employee_action(self):
        
        ma_nv = self.entry_manv.get().strip()
        ten_nv = self.entry_tennv.get().strip()
        sdt = self.entry_sdt.get().strip()
        dia_chi = self.entry_diachi.get().strip()
        
        if not all([ma_nv, ten_nv]):
            messagebox.showwarning("Thiếu Thông Tin", "Vui lòng nhập Mã NV và Tên Nhân Viên.")
            return
        
        if self.db_manager.insert_employee(ma_nv, ten_nv, sdt, dia_chi):
            self.load_employee_data()
            self.clear_employee_entries()
            messagebox.showinfo("Thành công", "Thêm nhân viên thành công!")
        else:
            messagebox.showerror("Lỗi", "Không thể thêm nhân viên.")
    
    def update_employee_action(self):
    
        if not hasattr(self, 'selected_ma_nv') or not self.selected_ma_nv:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên từ danh sách để sửa.")
            return
        
        ten_nv = self.entry_tennv.get().strip()
        sdt = self.entry_sdt.get().strip()
        dia_chi = self.entry_diachi.get().strip()
        
        if not ten_nv:
            messagebox.showwarning("Thiếu Thông Tin", "Vui lòng nhập tên nhân viên.")
            return
        
        if self.db_manager.update_employee(self.selected_ma_nv, ten_nv, sdt, dia_chi):
            self.load_employee_data()
            self.clear_employee_entries()
            messagebox.showinfo("Thành công", "Cập nhật nhân viên thành công!")
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật nhân viên.")
    
    def delete_employee_action(self):
        if not hasattr(self, 'selected_ma_nv') or not self.selected_ma_nv:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên từ danh sách để xóa.")
            return
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn xóa nhân viên '{self.selected_ma_nv}' không?"):
            if self.db_manager.delete_employee(self.selected_ma_nv):
                self.load_employee_data()
                self.clear_employee_entries()
                messagebox.showinfo("Thành công", "Xóa nhân viên thành công!")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa nhân viên.")
    
    def create_invoice_detail_view(self):
        main_frame = ttk.Frame(self.tab_invoice_detail)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        frame_input = ttk.LabelFrame(main_frame, text="THÔNG TIN CHI TIẾT HÓA ĐƠN", padding=(10, 5))
        frame_input.pack(side="left", fill="y", padx=10, pady=10)
        input_grid = ttk.Frame(frame_input)
        input_grid.pack(padx=10, pady=10)
        
        ttk.Label(input_grid, text="Mã Hóa Đơn:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_mahd = ttk.Entry(input_grid, width=30)
        self.entry_mahd.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_grid, text="Mã Vật Tư:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_mavt_detail = ttk.Entry(input_grid, width=30)
        self.entry_mavt_detail.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_grid, text="Số Lượng Bán:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_soluong_ban = ttk.Entry(input_grid, width=30)
        self.entry_soluong_ban.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(input_grid, text="Đơn Giá Bán:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_dongia_ban = ttk.Entry(input_grid, width=30)
        self.entry_dongia_ban.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(input_grid, text="Thành Tiền:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.entry_thanh_tien = ttk.Entry(input_grid, width=30, state='readonly')
        self.entry_thanh_tien.grid(row=4, column=1, padx=5, pady=5)
        
        frame_buttons = ttk.Frame(frame_input)
        frame_buttons.pack(pady=20, fill="x")
        ttk.Button(frame_buttons, text="Thêm", command=self.add_invoice_detail_action).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Sửa", command=self.update_invoice_detail_action).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Xóa", command=self.delete_invoice_detail_action).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Hủy", command=self.clear_invoice_detail_entries).pack(side="left", padx=5)
        
        frame_table = ttk.LabelFrame(main_frame, text="DANH SÁCH CHI TIẾT HÓA ĐƠN", padding=(10, 5))
        frame_table.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        cols = ("MaHD", "MaVT", "SoLuongBan", "DonGiaBan", "ThanhTien")
        self.invoice_detail_tree = ttk.Treeview(frame_table, columns=cols, show="headings")
        self.invoice_detail_tree.heading("MaHD", text="Mã HĐ")
        self.invoice_detail_tree.heading("MaVT", text="Mã VT")
        self.invoice_detail_tree.heading("SoLuongBan", text="SL Bán")
        self.invoice_detail_tree.heading("DonGiaBan", text="Đơn Giá")
        self.invoice_detail_tree.heading("ThanhTien", text="Thành Tiền")
        self.invoice_detail_tree.column("MaHD", width=80, anchor=tk.CENTER)
        self.invoice_detail_tree.column("MaVT", width=80, anchor=tk.CENTER)
        self.invoice_detail_tree.column("SoLuongBan", width=100, anchor=tk.CENTER)
        self.invoice_detail_tree.column("DonGiaBan", width=120, anchor='e')
        self.invoice_detail_tree.column("ThanhTien", width=120, anchor='e')
        vsb = ttk.Scrollbar(frame_table, orient="vertical", command=self.invoice_detail_tree.yview)
        vsb.pack(side="right", fill="y")
        self.invoice_detail_tree.configure(yscrollcommand=vsb.set)
        self.invoice_detail_tree.pack(fill="both", expand=True)
        self.invoice_detail_tree.bind("<<TreeviewSelect>>", self.on_invoice_detail_select)
        ttk.Button(frame_table, text="Tải lại Danh sách", command=self.load_invoice_detail_data).pack(pady=5)
        self.selected_invoice_key = None

        
        try:
            self.entry_soluong_ban.bind('<KeyRelease>', lambda e: self._compute_thanh_tien())
            self.entry_dongia_ban.bind('<KeyRelease>', lambda e: self._compute_thanh_tien())
        except Exception:
            pass

    def _compute_thanh_tien(self):
        s = self.entry_soluong_ban.get().strip()
        d = self.entry_dongia_ban.get().strip()
        try:
            so_luong = int(s) if s != '' else 0
            don_gia = float(d) if d != '' else 0.0
            thanh = so_luong * don_gia
            self.entry_thanh_tien.config(state='normal')
            self.entry_thanh_tien.delete(0, tk.END)
            self.entry_thanh_tien.insert(0, self._format_money(thanh))
            self.entry_thanh_tien.config(state='readonly')
        except Exception:
            self.entry_thanh_tien.config(state='normal')
            self.entry_thanh_tien.delete(0, tk.END)
            self.entry_thanh_tien.insert(0, "")
            self.entry_thanh_tien.config(state='readonly')

    def _format_money(self, value):
        """Định dạng số thành chuỗi có phân nghìn bằng dấu chấm (ví dụ 1234000 -> '1.234.000').
        Nếu value là None hoặc chuỗi rỗng trả về ''."""
        try:
            if value is None or value == '':
                return ''
            v = float(value)
        except Exception:
            return str(value)
        # Nếu là số nguyên, hiển thị không có phần thập phân
        try:
            if float(v).is_integer():
                return f"{int(v):,}".replace(",", ".")
            else:
                # hiển thị 2 chữ số thập phân khi cần
                return f"{v:,.2f}".replace(",", ".")
        except Exception:
            return str(value)

    def _parse_money_display(self, s):
        """Chuyển chuỗi đã format (vd '1.234.000') về float/int để xử lý.
        Bỏ dấu phân nghìn (dấu chấm) trước khi cast.
        """
        if s is None:
            return 0.0
        if isinstance(s, (int, float)):
            return float(s)
        t = str(s).strip()
        if t == '':
            return 0.0
        # loại bỏ tất cả dấu chấm (dùng làm phân nghìn)
        t2 = t.replace('.', '')
        # nếu còn dấu phẩy là dấu thập phân (hiếm khi xảy ra ở code này), thay bằng '.'
        t2 = t2.replace(',', '.')
        try:
            return float(t2)
        except Exception:
            return 0.0
    
    def load_invoice_detail_data(self):
        for item in self.invoice_detail_tree.get_children():
            self.invoice_detail_tree.delete(item)
        data = self.db_manager.fetch_all_invoice_details()
        for row in data:
            vals = self._clean_row(row, expected_len=5)
            # ensure variables initialized to avoid UnboundLocalError
            so_luong = 0
            don_gia = 0.0
            thanh_tien = ''
            # parse so_luong
            if len(vals) > 2 and vals[2] != '':
                try:
                    so_luong = int(vals[2])
                except Exception:
                    try:
                        so_luong = int(float(vals[2]))
                    except Exception:
                        so_luong = 0
            # parse don_gia
            if len(vals) > 3 and vals[3] != '':
                try:
                    don_gia = float(vals[3])
                except Exception:
                    don_gia = 0.0
            # determine thanh_tien
            if len(vals) > 4 and vals[4] != '' and vals[4] is not None:
                try:
                    thanh_tien = float(vals[4])
                except Exception:
                    thanh_tien = vals[4]
            else:
                try:
                    thanh_tien = so_luong * don_gia
                except Exception:
                    thanh_tien = ''
            # Hiển thị DonGia và ThanhTien đã format (với phân nghìn) trong Treeview
            display_don_gia = self._format_money(don_gia)
            display_thanh_tien = self._format_money(thanh_tien)
            self.invoice_detail_tree.insert("", tk.END, values=(vals[0], vals[1], so_luong, display_don_gia, display_thanh_tien))
    
    def on_invoice_detail_select(self, event):
        
        sel = self.invoice_detail_tree.selection()
        if not sel:
            return
        item = self.invoice_detail_tree.item(sel[0])
        vals = item.get("values", [])
        if not vals:
            return
        self.selected_invoice_key = (str(vals[0]), str(vals[1])) 
        self.entry_mahd.delete(0, tk.END)
        self.entry_mahd.insert(0, vals[0] if len(vals) > 0 else "")
        self.entry_mavt_detail.delete(0, tk.END)
        self.entry_mavt_detail.insert(0, vals[1] if len(vals) > 1 else "")
        self.entry_soluong_ban.delete(0, tk.END)
        self.entry_soluong_ban.insert(0, vals[2] if len(vals) > 2 else "")
        # vals[3] có thể là chuỗi đã format (có dấu chấm), cần parse về số trước khi đặt vào Entry để người dùng sửa dễ dàng
        raw_don_gia = vals[3] if len(vals) > 3 else ''
        parsed_don_gia = self._parse_money_display(raw_don_gia)
        self.entry_dongia_ban.delete(0, tk.END)
        # hiển thị dạng số thô (không có phân nghìn) để thuận tiện nhập/sửa
        if parsed_don_gia.is_integer():
            self.entry_dongia_ban.insert(0, str(int(parsed_don_gia)))
        else:
            self.entry_dongia_ban.insert(0, str(parsed_don_gia))
       
        try:
            self._compute_thanh_tien()
        except Exception:
            pass
    
    def clear_invoice_detail_entries(self):
       
        self.entry_mahd.delete(0, tk.END)
        self.entry_mavt_detail.delete(0, tk.END)
        self.entry_soluong_ban.delete(0, tk.END)
        self.entry_dongia_ban.delete(0, tk.END)
        try:
            self.entry_thanh_tien.config(state='normal')
            self.entry_thanh_tien.delete(0, tk.END)
            self.entry_thanh_tien.config(state='readonly')
        except Exception:
            pass
        self.selected_invoice_key = None
    
    def add_invoice_detail_action(self):
       
        ma_hd = self.entry_mahd.get().strip()
        ma_vt = self.entry_mavt_detail.get().strip()
        so_luong_str = self.entry_soluong_ban.get().strip()
        don_gia_str = self.entry_dongia_ban.get().strip()
        
        if not all([ma_hd, ma_vt, so_luong_str, don_gia_str]):
            messagebox.showwarning("Thiếu Thông Tin", "Vui lòng điền đủ tất cả các trường.")
            return
        
        try:
            so_luong = int(so_luong_str)
            don_gia = float(don_gia_str)
        except ValueError:
            messagebox.showerror("Lỗi Dữ Liệu", "Số Lượng phải là số nguyên, Đơn Giá phải là số.")
            return
        
        materials = self.db_manager.fetch_all_materials()
        if not any(str(m[0]).lower() == ma_vt.lower() for m in materials):
            messagebox.showerror("Lỗi Mã Vật Tư", f"Mã Vật Tư '{ma_vt}' không tồn tại. Vui lòng kiểm tra danh sách Vật Tư.")
            return

        
        if not self.db_manager.invoice_exists(ma_hd):
            create = messagebox.askyesno("Hóa Đơn chưa tồn tại", f"Mã Hóa Đơn '{ma_hd}' chưa tồn tại. Bạn có muốn tạo Hóa Đơn mới với MaHD này không?")
            if not create:
                return
            
            ma_nv_for_invoice = simpledialog.askstring("Tạo Hóa Đơn", "Nhập Mã NV (Người lập) cho Hóa Đơn mới:")
            if not ma_nv_for_invoice:
                messagebox.showwarning("Hủy", "Không có Mã NV được cung cấp. Hủy tạo Hóa Đơn.")
                return
            ok_invoice = self.db_manager.insert_invoice(ma_hd, ma_nv_for_invoice.strip())
            if not ok_invoice:
                messagebox.showerror("Lỗi", "Không thể tạo Hóa Đơn mới. Kiểm tra kết nối hoặc dữ liệu.")
                return
        # Tránh insert trùng (khóa chính): nếu đã có, hỏi cập nhật
        try:
            if self.db_manager.invoice_detail_exists(ma_hd, ma_vt):
                upd = messagebox.askyesno("Đã tồn tại", "Chi tiết này đã tồn tại. Bạn có muốn cập nhật Số Lượng/Đơn Giá không?")
                if upd:
                    if self.db_manager.update_invoice_detail(ma_hd, ma_vt, so_luong, don_gia):
                        self.load_invoice_detail_data()
                        self.clear_invoice_detail_entries()
                        messagebox.showinfo("Thành công", "Cập nhật chi tiết hóa đơn thành công!")
                    else:
                        messagebox.showerror("Lỗi", "Không thể cập nhật chi tiết hóa đơn.")
                return
        except Exception:
            # nếu lỗi khi kiểm tra tồn tại, tiếp tục cố gắng insert và xử lý lỗi từ DB
            pass

        if self.db_manager.insert_invoice_detail(ma_hd, ma_vt, so_luong, don_gia):
            self.load_invoice_detail_data()
            self.clear_invoice_detail_entries()
            messagebox.showinfo("Thành công", "Thêm chi tiết hóa đơn thành công!")
        else:
            messagebox.showerror("Lỗi", "Không thể thêm chi tiết hóa đơn.")
    
    def update_invoice_detail_action(self):
        
        if not self.selected_invoice_key:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn chi tiết hóa đơn từ danh sách để sửa.")
            return
        
        so_luong_str = self.entry_soluong_ban.get().strip()
        don_gia_str = self.entry_dongia_ban.get().strip()
        
        if not all([so_luong_str, don_gia_str]):
            messagebox.showwarning("Thiếu Thông Tin", "Vui lòng điền đủ Số Lượng và Đơn Giá.")
            return
        
        try:
            so_luong = int(so_luong_str)
            don_gia = float(don_gia_str)
        except ValueError:
            messagebox.showerror("Lỗi Dữ Liệu", "Số Lượng phải là số nguyên, Đơn Giá phải là số.")
            return
        
        ma_hd, ma_vt = self.selected_invoice_key
        ma_hd = str(ma_hd).strip()
        ma_vt = str(ma_vt).strip()
        if self.db_manager.update_invoice_detail(ma_hd, ma_vt, so_luong, don_gia):
            self.load_invoice_detail_data()
            self.clear_invoice_detail_entries()
            messagebox.showinfo("Thành công", "Cập nhật chi tiết hóa đơn thành công!")
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật chi tiết hóa đơn.")
    
    def delete_invoice_detail_action(self):
        
        if not self.selected_invoice_key:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn chi tiết hóa đơn từ danh sách để xóa.")
            return
        
        ma_hd, ma_vt = self.selected_invoice_key
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn xóa chi tiết hóa đơn (HĐ: {ma_hd}, VT: {ma_vt}) không?"):
            if self.db_manager.delete_invoice_detail(ma_hd, ma_vt):
                self.load_invoice_detail_data()
                self.clear_invoice_detail_entries()
                messagebox.showinfo("Thành công", "Xóa chi tiết hóa đơn thành công!")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa chi tiết hóa đơn.")

if __name__ == "__main__":
    app = StoreApp()
    app.mainloop()