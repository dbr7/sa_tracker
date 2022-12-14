import json, os, html
from scholarly import scholarly, ProxyGenerator

is_save = True
out_rank_path = "./rank.csv"
icse_2019_data_path = "./data/icse_2019.json"

def load_papers_from_json(json_path):
    with open(json_path, "r") as f:
        paper_data = json.load(f)

    papers = paper_data["result"]["hits"]["hit"]
    r = []
    for paper in papers:
        title = paper["info"]["title"]
        r.append(title)

    return r


def fetch(target_paper_title, is_save=False):    
    search_query = scholarly.search_pubs(target_paper_title)
    paper = scholarly.fill(next(search_query))

    num_citation = paper["num_citations"]
    title = paper["bib"]["title"]  

    if "booktitle" in paper["bib"]:
        venue = paper["bib"]["booktitle"]
    else:
        print("This has a prob")
        venue = paper["bib"]["venue"]

       
    print(title)
    print(venue)
    print(num_citation)

    if is_save:
        with open(out_rank_path, "a") as f:
            f.write(f"{title},{num_citation}\n")



if __name__ == "__main__":
    if is_save and os.path.exists(out_rank_path):
        os.remove(out_rank_path)

    pg = ProxyGenerator()
    success = pg.FreeProxies()
    scholarly.use_proxy(pg)

    icse_2019_papers = load_papers_from_json(icse_2019_data_path)

    for _p in icse_2019_papers:    
        _p = html.unescape(_p)
        print("="*30)
        print(f"Fetching '{_p}'")
        fetch(_p, is_save=is_save)
        # break