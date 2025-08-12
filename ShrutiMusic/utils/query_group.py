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
