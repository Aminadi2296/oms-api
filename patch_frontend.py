path = r'c:\Projects\oms\src\hooks\usePaginatedResource.ts'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = """        const raw = await fetchApi<RawPaginatedResponse>(url)

        const items = Array.isArray(raw?.[dataKey]) ? (raw[dataKey] as T[]) : []

        // Use the pagination data directly from the API response
        const apiTotal = raw.total || 0
        const apiPages = raw.pages || 1"""

replacement = """        const raw = await fetchApi<RawPaginatedResponse>(url)

        const items = Array.isArray(raw?.[dataKey])
          ? (raw[dataKey] as T[])
          : Array.isArray(raw?.data)
          ? (raw.data as T[])
          : []

        // Use the pagination data directly from the API response
        const apiTotal = raw?.total ?? raw?.meta?.total ?? 0
        const apiPages = raw?.pages ?? raw?.meta?.last_page ?? 1"""

if target in c:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c.replace(target, replacement))
    print("PATCH_PAGINATED_RESOURCE: SUCCESS")
else:
    # Try normalizing newlines
    c_norm = c.replace('\r\n', '\n')
    if target in c_norm:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c_norm.replace(target, replacement))
        print("PATCH_PAGINATED_RESOURCE: SUCCESS_NORM")
    else:
        print("PATCH_PAGINATED_RESOURCE: NOT FOUND")
