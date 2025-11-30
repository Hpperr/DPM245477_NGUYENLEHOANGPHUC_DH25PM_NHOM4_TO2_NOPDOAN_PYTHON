-- 1. B?ng NHANVIEN (Qu?n lý Nhân viên)
IF OBJECT_ID('NhanVien', 'U') IS NOT NULL
    DROP TABLE NhanVien;
CREATE TABLE NhanVien (
    MaNV VARCHAR(10) PRIMARY KEY, 
    TenNV NVARCHAR(100) NOT NULL,
    SDT VARCHAR(15),
    DiaChi NVARCHAR(255),
    NgayVaoLam DATE DEFAULT GETDATE()
)
-- 2 B?ng VATTU (Qu?n lý V?t t?/Hàng t?n kho)
IF OBJECT_ID('VatTu', 'U') IS NOT NULL
    DROP TABLE VatTu;
CREATE TABLE VatTu (
    MaVT VARCHAR(15) PRIMARY KEY, 
    TenVT NVARCHAR(150) NOT NULL UNIQUE, 
    DonVi NVARCHAR(50), 
    SoLuongTon INT NOT NULL DEFAULT 0, 
    DonGiaBan DECIMAL(18, 0)
)
-- 3 B?ng HOADON (Qu?n lý Hóa ??n - Thông tin chung)
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

-- 4 B?ng CHITIETHOADON (Chi ti?t các m?t hàng trong t?ng Hóa ??n)
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

-- Thêm d? li?u m?u cho Nhân Viên
INSERT INTO NhanVien (MaNV, TenNV, SDT, DiaChi) VALUES
('NV001', N'Nguy?n V?n A', '0912345678', N'123 ???ng Lê L?i, TP.HCM'),
('NV002', N'Tr?n Th? B', '0923456789', N'456 ???ng Nguy?n Hu?, TP.HCM'),
('NV003', N'Ph?m V?n C', '0934567890', N'789 ???ng Tr?n H?ng ??o, Hà N?i'),
('NV004', N'Lê Th? D', '0945678901', N'321 ???ng Cách M?ng Tháng Tám, TP.HCM'),
('NV005', N'Hoàng V?n E', '0956789012', N'654 ???ng Pasteur, TP.HCM'),
('NV006', N'Võ Th? F', '0967890123', N'987 ???ng Nguy?n Th? Minh Khai, Hà N?i')