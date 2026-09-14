from duckduckgo_search import DDGS
import json

with DDGS() as ddgs:
    results = ddgs.images("Waree Onsen & Hot Spring Spa Chiang Mai", max_results=1)
    print(json.dumps(results, indent=2))
