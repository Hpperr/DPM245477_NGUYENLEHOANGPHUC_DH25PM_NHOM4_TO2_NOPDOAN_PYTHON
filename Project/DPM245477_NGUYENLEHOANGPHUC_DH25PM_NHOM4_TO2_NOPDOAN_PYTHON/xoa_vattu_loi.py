import pyodbc
SERVER = 'DESKTOP-9FLA8Q5\\SQLEXPRESS'
DATABASE = 'model'
USERNAME = 'sa'
PASSWORD = 'sql2025'

EXACT_FILTER = ('C74EB1ED', 's', 't', '30')


def connect():
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};DATABASE={DATABASE};"
        f"UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes"
    )
    return pyodbc.connect(conn_str)


def find_rows(cursor, m, t, dv, sl):

    cursor.execute(
      
        (m, t, dv, str(sl))
    )
    return cursor.fetchall()


def broad_search(cursor):
    cursor.execute(
        
        ('%C74EB1ED%', '%s%', '%t%', '%30%')
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
        m, t, dv, sl = r
        cur.execute(
            (m, t, dv, sl)
        )
        deleted += 1
    conn.commit()
    print(f'Đã xóa {deleted} bản ghi.')
    conn.close()


if __name__ == '__main__':
    main()
