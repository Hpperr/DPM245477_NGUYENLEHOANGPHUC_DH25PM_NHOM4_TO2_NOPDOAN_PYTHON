class DBManager:
    """Lớp quản lý cơ sở dữ liệu SQL Server"""
    
    def __init__(self, server, database, username, password):
        """Khởi tạo kết nối cơ sở dữ liệu SQL Server"""
        # Use the provided parameters (do not hardcode)
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        self.connect()

    def connect(self):
        """Thiết lập kết nối tới SQL Server"""
        try:
            import pyodbc
            connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password};TrustServerCertificate=yes'
            self.connection = pyodbc.connect(connection_string)
            print(f"Kết nối cơ sở dữ liệu '{self.database}' thành công!")
        except ImportError:
            print("Cảnh báo: pyodbc chưa được cài đặt. Chạy: pip install pyodbc")
            self.connection = None
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            self.connection = None

    def fetch_all_materials(self):
        """Lấy tất cả vật tư từ cơ sở dữ liệu"""
        try:
            if not self.connection:
                return []
            cursor = self.connection.cursor()
            cursor.execute("SELECT MaVT, TenVT, DonVi, SoLuongTon FROM VatTu")
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"✗ Lỗi lấy dữ liệu: {e}")
            return []

    def insert_material(self, ma_vt, ten_vt, don_vi, so_luong):
        """Thêm mới vật tư vào cơ sở dữ liệu"""
        try:
            if not self.connection:
                print("Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO VatTu (MaVT, TenVT, DonVi, SoLuongTon) VALUES (?, ?, ?, ?)",
                (ma_vt, ten_vt, don_vi, so_luong)
            )
            self.connection.commit()
            cursor.close()
            print(f"Thêm vật tư '{ten_vt}' thành công!")
            return True
        except Exception as e:
            print(f"Lỗi thêm dữ liệu: {e}")
            return False

    def update_material(self, ma_vt, ten_vt, don_vi, so_luong):
        """Cập nhật thông tin vật tư"""
        try:
            if not self.connection:
                print("Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE VatTu SET TenVT=?, DonVi=?, SoLuongTon=? WHERE MaVT=?",
                (ten_vt, don_vi, so_luong, ma_vt)
            )
            self.connection.commit()
            cursor.close()
            print(f"Cập nhật vật tư '{ma_vt}' thành công!")
            return True
        except Exception as e:
            print(f"Lỗi cập nhật: {e}")
            return False

    def delete_material(self, ma_vt):
        """Xóa vật tư từ cơ sở dữ liệu"""
        try:
            if not self.connection:
                print("✗ Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM VatTu WHERE MaVT=?", (ma_vt,))
            self.connection.commit()
            cursor.close()
            print(f"Xóa vật tư '{ma_vt}' thành công!")
            return True
        except Exception as e:
            print(f"Lỗi xóa: {e}")
            return False

    def close(self):
        """Đóng kết nối cơ sở dữ liệu"""
        if self.connection:
            self.connection.close()
            print("Kết nối cơ sở dữ liệu đã đóng!")

    # ---------- Nhân viên (NhanVien) CRUD ----------
    def fetch_all_employees(self):
        try:
            if not self.connection:
                return []
            cursor = self.connection.cursor()
            cursor.execute("SELECT MaNV, TenNV, SDT, DiaChi FROM NhanVien")
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"✗ Lỗi lấy danh sách nhân viên: {e}")
            return []

    def insert_employee(self, ma_nv, ten_nv, sdt, dia_chi):
        try:
            if not self.connection:
                print("Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO NhanVien (MaNV, TenNV, SDT, DiaChi) VALUES (?, ?, ?, ?)",
                (ma_nv, ten_nv, sdt, dia_chi)
            )
            self.connection.commit()
            cursor.close()
            print(f"Thêm nhân viên '{ma_nv}' thành công!")
            return True
        except Exception as e:
            print(f"Lỗi thêm nhân viên: {e}")
            return False

    def update_employee(self, ma_nv, ten_nv, sdt, dia_chi):
        try:
            if not self.connection:
                print("Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE NhanVien SET TenNV=?, SDT=?, DiaChi=? WHERE MaNV=?",
                (ten_nv, sdt, dia_chi, ma_nv)
            )
            self.connection.commit()
            cursor.close()
            print(f"Cập nhật nhân viên '{ma_nv}' thành công!")
            return True
        except Exception as e:
            print(f"Lỗi cập nhật nhân viên: {e}")
            return False

    def delete_employee(self, ma_nv):
        try:
            if not self.connection:
                print("Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM NhanVien WHERE MaNV=?", (ma_nv,))
            self.connection.commit()
            cursor.close()
            print(f"Xóa nhân viên '{ma_nv}' thành công!")
            return True
        except Exception as e:
            print(f"Lỗi xóa nhân viên: {e}")
            return False

    # ---------- Chi tiết hóa đơn (ChiTietHoaDon) CRUD ----------
    def fetch_all_invoice_details(self):
        try:
            if not self.connection:
                return []
            cursor = self.connection.cursor()
            cursor.execute("SELECT MaHD, MaVT, SoLuongBan, DonGiaBan, ThanhTien FROM ChiTietHoaDon")
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"✗ Lỗi lấy chi tiết hóa đơn: {e}")
            return []

    def insert_invoice_detail(self, ma_hd, ma_vt, so_luong, don_gia):
        try:
            if not self.connection:
                print("Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            # Kiểm tra mã vật tư tồn tại
            cursor.execute("SELECT 1 FROM VatTu WHERE MaVT=?", (ma_vt,))
            if not cursor.fetchone():
                print(f"✗ Mã Vật Tư '{ma_vt}' không tồn tại.")
                cursor.close()
                return False
            # Kiểm tra mã hóa đơn tồn tại
            cursor.execute("SELECT MaHD FROM HoaDon WHERE MaHD=?", (ma_hd,))
            if not cursor.fetchone():
                print(f"✗ Mã Hóa Đơn '{ma_hd}' chưa tồn tại. Vui lòng tạo Hóa Đơn trước khi thêm chi tiết.")
                cursor.close()
                return False
            # Thêm chi tiết
            cursor.execute(
                "INSERT INTO ChiTietHoaDon (MaHD, MaVT, SoLuongBan, DonGiaBan) VALUES (?, ?, ?, ?)",
                (ma_hd, ma_vt, int(so_luong), float(don_gia))
            )
            self.connection.commit()
            cursor.close()
            print(f"Thêm chi tiết HĐ (HĐ={ma_hd}, VT={ma_vt}) thành công!")
            return True
        except Exception as e:
            print(f"Lỗi thêm chi tiết hóa đơn: {e}")
            return False

    def update_invoice_detail(self, ma_hd, ma_vt, so_luong, don_gia):
        try:
            if not self.connection:
                print("Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE ChiTietHoaDon SET SoLuongBan=?, DonGiaBan=? WHERE MaHD=? AND MaVT=?",
                (int(so_luong), float(don_gia), ma_hd, ma_vt)
            )
            self.connection.commit()
            cursor.close()
            print(f"Cập nhật chi tiết HĐ (HĐ={ma_hd}, VT={ma_vt}) thành công!")
            return True
        except Exception as e:
            print(f"Lỗi cập nhật chi tiết hóa đơn: {e}")
            return False

    def delete_invoice_detail(self, ma_hd, ma_vt):
        try:
            if not self.connection:
                print("Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM ChiTietHoaDon WHERE MaHD=? AND MaVT=?", (ma_hd, ma_vt))
            self.connection.commit()
            cursor.close()
            print(f"Xóa chi tiết HĐ (HĐ={ma_hd}, VT={ma_vt}) thành công!")
            return True
        except Exception as e:
            print(f"Lỗi xóa chi tiết hóa đơn: {e}")
            return False
        
    # ---------- Hàm hỗ trợ cho Hóa Đơn ----------
    def invoice_exists(self, ma_hd):
        """Kiểm tra xem một MaHD có tồn tại trong bảng HoaDon hay không."""
        try:
            if not self.connection:
                return False
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM HoaDon WHERE MaHD=?", (ma_hd,))
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        except Exception as e:
            print(f"Lỗi kiểm tra HoaDon: {e}")
            return False

    def insert_invoice(self, ma_hd, ma_nv):
        """Tạo một bản ghi HoaDon mới với MaHD và MaNV (Ngày lập mặc định)."""
        try:
            if not self.connection:
                print("Không có kết nối cơ sở dữ liệu")
                return False
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO HoaDon (MaHD, MaNV) VALUES (?, ?)",
                (ma_hd, ma_nv)
            )
            self.connection.commit()
            cursor.close()
            print(f"Tạo HoaDon mới MaHD={ma_hd}, MaNV={ma_nv} thành công")
            return True
        except Exception as e:
            print(f"Lỗi tạo HoaDon: {e}")
            return False

    def invoice_detail_exists(self, ma_hd, ma_vt):
        """Kiểm tra xem một chi tiết hóa đơn (MaHD, MaVT) đã tồn tại hay chưa."""
        try:
            if not self.connection:
                return False
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM ChiTietHoaDon WHERE MaHD=? AND MaVT=?", (ma_hd, ma_vt))
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        except Exception as e:
            print(f"Lỗi kiểm tra ChiTietHoaDon: {e}")
            return False
