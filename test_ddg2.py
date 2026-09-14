from duckduckgo_search import DDGS
print("Starting search...")
try:
    with DDGS() as ddgs:
        res = list(ddgs.images("Waree Onsen Chiang Mai", max_results=1))
        print("Result:", res)
except Exception as e:
    print("Error:", e)
