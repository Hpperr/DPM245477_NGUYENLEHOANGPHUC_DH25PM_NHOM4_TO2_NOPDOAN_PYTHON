import pyodbc
SERVER = 'DESKTOP-9FLA8Q5\\SQLEXPRESS'
DATABASE = 'model'
USERNAME = 'sa'
PASSWORD = 'sql2025'

EXACT_FILTER = ('A1', 'A', '435436', 'SDF')

def connect():
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};DATABASE={DATABASE};"
        f"UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes"
    )
    return pyodbc.connect(conn_str)


def find_rows(cursor, m, t, s, d):
    cursor.execute(
        "SELECT MaNV, TenNV, SDT, DiaChi FROM NhanVien WHERE MaNV=? AND TenNV=? AND SDT=? AND DiaChi=?",
        (m, t, s, d)
    )
    return cursor.fetchall()


def broad_search(cursor):
    cursor.execute(
        "SELECT MaNV, TenNV, SDT, DiaChi FROM NhanVien WHERE MaNV LIKE ? OR TenNV LIKE ? OR SDT LIKE ? OR DiaChi LIKE ?",
        ('%A1%', '%A%', '%435436%', '%SDF%')
    )
    return cursor.fetchall()


def main():
    try:
        conn = connect()
    except Exception as e:
        print('Kết nối thất bại:', e)
        return
    cur = conn.cursor()

    rows = find_rows(cur, *EXACT_FILTER)
    if not rows:
        print('Không tìm thấy bản ghi chính xác. Thử tìm bằng like...')
        rows = broad_search(cur)

    if not rows:
        print('Không tìm thấy bản ghi nào phù hợp.')
        conn.close()
        return

    print('Các bản ghi tìm thấy:')
    for r in rows:
        print(tuple(r))

    confirm = input('Có chắc muốn xóa bản ghi trên không? ( y ): ').strip().lower()
    if confirm != 'y':
        print('Hủy bỏ. Không xóa.')
        conn.close()
        return

    deleted = 0
    for r in rows:
        m, t, s, d = r
        print(f"Xử lý xóa nhân viên: MaNV={m}, TenNV={t}, SDT={s}, DiaChi={d}")
        # Kiểm tra xem có hóa đơn tham chiếu tới nhân viên này không
        cur.execute("SELECT MaHD FROM HoaDon WHERE MaNV=?", (m,))
        invoices = cur.fetchall()
        if invoices:
            print(f"Phát hiện {len(invoices)} hóa đơn liên quan:")
            inv_list = [row[0] for row in invoices]
            for ih in inv_list:
                print(" -", ih)
            # Hỏi người dùng hành động: xóa phụ thuộc, gán lại, hoặc hủy
            action = input("Chọn hành động: (d)elete các Hóa Đơn & Chi Tiết; (r)eassign Hóa Đơn cho NV khác; (c)ancel xóa nhân viên: ").strip().lower()
            if action == 'c' or action == 'cancel':
                print('Bỏ qua xóa nhân viên này.')
                continue
            if action == 'r' or action == 'reassign':
                new_manv = input('Nhập MaNV mới để gán các Hóa Đơn (phải tồn tại): ').strip()
                if not new_manv:
                    print('Không cung cấp MaNV mới. Bỏ qua xóa nhân viên này.')
                    continue
                # kiểm tra MaNV mới tồn tại
                cur.execute('SELECT 1 FROM NhanVien WHERE MaNV=?', (new_manv,))
                if not cur.fetchone():
                    print(f'Mã NV "{new_manv}" không tồn tại. Bỏ qua xóa nhân viên này.')
                    continue
                # cập nhật MaNV trên HoaDon
                cur.execute('UPDATE HoaDon SET MaNV=? WHERE MaNV=?', (new_manv, m))
                print(f'Đã gán {len(inv_list)} hóa đơn sang MaNV={new_manv}.')
            elif action == 'd' or action == 'delete':
                # xóa chi tiết trước
                for ih in inv_list:
                    try:
                        cur.execute('DELETE FROM ChiTietHoaDon WHERE MaHD=?', (ih,))
                    except Exception as e:
                        print('Lỗi khi xóa ChiTietHoaDon cho', ih, e)
                # xóa hóa đơn
                try:
                    cur.execute('DELETE FROM HoaDon WHERE MaNV=?', (m,))
                except Exception as e:
                    print('Lỗi khi xóa HoaDon cho MaNV', m, e)
                print(f'Đã xóa {len(inv_list)} hóa đơn và chi tiết liên quan.')
            else:
                print('Lựa chọn không hợp lệ. Bỏ qua xóa nhân viên này.')
                continue

        # Nếu không còn ràng buộc, thực hiện xóa nhân viên
        try:
            cur.execute("DELETE FROM NhanVien WHERE MaNV=? AND TenNV=? AND SDT=? AND DiaChi=?", (m, t, s, d))
            if cur.rowcount and cur.rowcount > 0:
                deleted += 1
                print(f'Đã xóa nhân viên {m}.')
            else:
                print(f'Không xóa được nhân viên {m} (không tìm thấy hàng khớp).')
        except Exception as e:
            print('Lỗi xóa nhân viên:', e)
            # không raise, tiếp tục xử lý các bản ghi khác
            continue

    conn.commit()
    print(f'Hoàn tất. Đã xóa {deleted} bản ghi nhân viên (nếu có).')
    conn.close()

if __name__ == '__main__':
    main()
