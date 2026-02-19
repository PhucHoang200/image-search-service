import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-DE6G2CH\SQLEXPRESS;"
    "DATABASE=fashion_shop;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def get_connection():
    return pyodbc.connect(CONN_STR)


def get_products_by_ids(sanpham_ids):
    if not sanpham_ids:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in sanpham_ids)

    sql = f"""
    SELECT
        sp.SanPhamID,
        sp.TenSanPham,
        MIN(bt.GiaBan) AS GiaBan,
        COALESCE(img.URL, '') AS UrlAnh
    FROM SanPham sp
    JOIN SanPham_BienThe bt ON sp.SanPhamID = bt.SanPhamID
    LEFT JOIN AnhSanPham img
        ON sp.SanPhamID = img.SanPhamID
        AND img.IsPrimary = 1
    WHERE sp.SanPhamID IN ({placeholders})
    GROUP BY sp.SanPhamID, sp.TenSanPham, img.URL
    """

    cursor.execute(sql, sanpham_ids)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "SanPhamID": r.SanPhamID,
            "TenSanPham": r.TenSanPham,
            "GiaBan": float(r.GiaBan),
            "UrlAnh": r.UrlAnh
        }
        for r in rows
    ]

def get_all_sanpham_ids():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SanPhamID FROM SanPham")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return set(r.SanPhamID for r in rows)

def get_fallback_products(exclude_ids=None, limit=10):
    exclude_ids = exclude_ids or []

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in exclude_ids)

    sql = f"""
    SELECT TOP {limit}
        sp.SanPhamID,
        sp.TenSanPham,
        MIN(bt.GiaBan) AS GiaBan,
        COALESCE(img.URL, '') AS UrlAnh
    FROM SanPham sp
    JOIN SanPham_BienThe bt ON sp.SanPhamID = bt.SanPhamID
    LEFT JOIN AnhSanPham img 
        ON sp.SanPhamID = img.SanPhamID AND img.IsPrimary = 1
    {"WHERE sp.SanPhamID NOT IN (" + placeholders + ")" if exclude_ids else ""}
    GROUP BY sp.SanPhamID, sp.TenSanPham, img.URL
    ORDER BY NEWID()
    """

    cursor.execute(sql, exclude_ids)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "SanPhamID": r.SanPhamID,
            "TenSanPham": r.TenSanPham,
            "GiaBan": float(r.GiaBan),
            "UrlAnh": r.UrlAnh
        }
        for r in rows
    ]


def get_category_by_sanpham_id(sanpham_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT dm.DanhMucID, dm.PhanLoaiID
        FROM SanPham sp
        JOIN DanhMuc dm ON sp.DanhMucID = dm.DanhMucID
        WHERE sp.SanPhamID = ?
    """, sanpham_id)

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return row.DanhMucID, row.PhanLoaiID
    return None, None


def get_fallback_products_same_category(phan_loai_id, exclude_ids=None, limit=10):
    exclude_ids = exclude_ids or []

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in exclude_ids)

    sql = f"""
    SELECT TOP {limit}
        sp.SanPhamID,
        sp.TenSanPham,
        MIN(bt.GiaBan) AS GiaBan,
        COALESCE(img.URL, '') AS UrlAnh
    FROM SanPham sp
    JOIN DanhMuc dm ON sp.DanhMucID = dm.DanhMucID
    JOIN SanPham_BienThe bt ON sp.SanPhamID = bt.SanPhamID
    LEFT JOIN AnhSanPham img 
        ON sp.SanPhamID = img.SanPhamID AND img.IsPrimary = 1
    WHERE dm.PhanLoaiID = ?
    {"AND sp.SanPhamID NOT IN (" + placeholders + ")" if exclude_ids else ""}
    GROUP BY sp.SanPhamID, sp.TenSanPham, img.URL
    ORDER BY NEWID()
    """

    params = [phan_loai_id] + exclude_ids
    cursor.execute(sql, params)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "SanPhamID": r.SanPhamID,
            "TenSanPham": r.TenSanPham,
            "GiaBan": float(r.GiaBan),
            "UrlAnh": r.UrlAnh
        }
        for r in rows
    ]
