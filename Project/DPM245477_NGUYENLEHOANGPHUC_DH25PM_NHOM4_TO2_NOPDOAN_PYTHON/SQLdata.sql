-- 1. Bảng NHANVIEN (Quản lý Nhân viên)
IF OBJECT_ID('NhanVien', 'U') IS NOT NULL
    DROP TABLE NhanVien;
CREATE TABLE NhanVien (
    MaNV VARCHAR(10) PRIMARY KEY, 
    TenNV NVARCHAR(100) NOT NULL,
    SDT VARCHAR(15),
    DiaChi NVARCHAR(255),
    NgayVaoLam DATE DEFAULT GETDATE()
)
-- 2 Bảng VATTU (Quản lý Vật tư/Hàng tồn kho)
IF OBJECT_ID('VatTu', 'U') IS NOT NULL
    DROP TABLE VatTu;
CREATE TABLE VatTu (
    MaVT VARCHAR(15) PRIMARY KEY, 
    TenVT NVARCHAR(150) NOT NULL UNIQUE, 
    DonVi NVARCHAR(50), 
    SoLuongTon INT NOT NULL DEFAULT 0, 
    DonGiaBan DECIMAL(18, 0)
)
-- 3 Bảng HOADON (Quản lý Hóa đơn - Thông tin chung)
IF OBJECT_ID('HoaDon', 'U') IS NOT NULL
    DROP TABLE HoaDon;
CREATE TABLE HoaDon (
    MaHD VARCHAR(20) PRIMARY KEY, 
    MaNV VARCHAR(10) NOT NULL, 
    NgayLap DATE NOT NULL DEFAULT GETDATE(),
    TongTien DECIMAL(18, 0) DEFAULT 0,
    TrangThai NVARCHAR(50), 
    
    
    FOREIGN KEY (MaNV) REFERENCES NhanVien(MaNV)
)

-- 4 Bảng CHITIETHOADON (Chi tiết các mặt hàng trong từng Hóa đơn)
IF OBJECT_ID('ChiTietHoaDon', 'U') IS NOT NULL
    DROP TABLE ChiTietHoaDon;
CREATE TABLE ChiTietHoaDon (
    MaHD VARCHAR(20) NOT NULL, 
    MaVT VARCHAR(15) NOT NULL, 
    
    SoLuongBan INT NOT NULL,
    DonGiaBan DECIMAL(18, 0),
    ThanhTien AS (SoLuongBan * DonGiaBan), 
    PRIMARY KEY (MaHD, MaVT),
    FOREIGN KEY (MaHD) REFERENCES HoaDon(MaHD),
    FOREIGN KEY (MaVT) REFERENCES VatTu(MaVT)
)

