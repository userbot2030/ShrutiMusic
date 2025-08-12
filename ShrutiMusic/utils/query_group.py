# query_group.py
# Modul untuk fungsi-fungsi terkait pengelompokan query musik

def group_queries(queries):
    """
    Mengelompokkan list query berdasarkan kriteria tertentu.
    Parameter:
        queries (list): List query (string)
    Return:
        dict: Dictionary hasil pengelompokan
    """
    grouped = {}
    for query in queries:
        key = query[0].upper()  # contoh pengelompokan berdasarkan huruf awal
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(query)
    return grouped

def ankes_group(data):
    """
    Fungsi contoh untuk mengelompokkan data ankes (angket kesehatan/group).
    Ubah logika sesuai kebutuhan aplikasi kamu.
    """
    # Contoh logika: kelompokkan data berdasarkan field 'group'
    result = {}
    for item in data:
        key = item.get('group', 'lainnya')
        result.setdefault(key, []).append(item)
    return result

# Tambahkan fungsi lain jika dibutuhkan
