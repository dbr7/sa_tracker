import json, os, html, sqlite3, argparse

from scholarly import scholarly, ProxyGenerator
from datetime import datetime, timezone, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("--db-path", default="/home/sa_tracker/cite.db", type=str)
parser.add_argument("--paper-list", default="/home/sa_tracker/data/icse_2019.json", type=str)
parser.add_argument("--table-name", default="icse2019", type=str)
args = parser.parse_args()

DB_PATH = args.db_path
PAPER_LIST_PATH = args.paper_list
TABLE_NAME = args.table_name

timezone_korea = timezone(timedelta(hours=9))


def load_papers_from_json(json_path):
    with open(json_path, "r") as f:
        paper_data = json.load(f)

    papers = paper_data["result"]["hits"]["hit"]
    r = []
    for paper in papers:
        title = paper["info"]["title"]
        r.append(title)

    return r


def fetch(target_paper_title):    
    search_query = scholarly.search_pubs(target_paper_title)
    paper = scholarly.fill(next(search_query))
    
    num_citation = paper["num_citations"]
    title = paper["bib"]["title"]  
    bib_id = paper["bib"]["bib_id"]

    if "booktitle" in paper["bib"]:
        exact = 1
        venue = paper["bib"]["booktitle"]
    else:
        print("This has a prob")
        exact = 0
        venue = paper["bib"]["venue"]

    return bib_id, title, num_citation, exact


if __name__ == "__main__":    
    # Load papers
    papers = load_papers_from_json(PAPER_LIST_PATH)
    
    # DB lookup
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()    

    c.execute(f"SELECT * FROM {TABLE_NAME}")
    db_papers = c.fetchall()    

    # Set up a proxy    
    pg = ProxyGenerator()
    success = pg.FreeProxies()
    scholarly.use_proxy(pg)

    # c.execute(f"DELETE FROM {TABLE_NAME}")    
    current_time = datetime.now(timezone_korea)

    for json_p in papers:
        json_p = html.unescape(json_p)
        is_fetched = False
        for db_p in db_papers:
            _id, _title, _num_citation, _exact, _current_time, _jsontitle = db_p
            if json_p == _jsontitle:                
                is_fetched = True
                break
        
        if not is_fetched or (current_time - datetime.fromisoformat(_current_time)).total_seconds() > 60 * 60 * 12:
            print(f"Fetching '{json_p}'")
            p_id, p_title, p_num_citation, p_exact = fetch(json_p)
            
            print(p_id, p_title, json_p, p_num_citation, p_exact, current_time)
            c.execute(
                f"INSERT INTO {TABLE_NAME} (id, title, jsontitle, citation, exact, dt) VALUES (?, ?, ?, ?, ?, ?)",
                (p_id, p_title, json_p, p_num_citation, p_exact, current_time)
            )
            conn.commit()
