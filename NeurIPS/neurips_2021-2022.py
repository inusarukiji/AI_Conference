import openreview
import pandas as pd
import statistics
import sys

# =========================
# YEAR をターミナル引数から取得
# =========================
if len(sys.argv) < 2:
    print("使い方: python3 gemini_api.py 2024")
    sys.exit(1)

YEAR = sys.argv[1]
CONF = f"NeurIPS.cc/{YEAR}/Conference"
SUBMISSION_INV = f"{CONF}/-/Blind_Submission"

client = openreview.Client(baseurl="https://api.openreview.net")

print("YEAR:", YEAR)
print("CONF:", CONF)

print("=== submissions (directReplies付き) 取得中 ===")
submissions = client.get_all_notes(
    invitation=SUBMISSION_INV,
    details="directReplies"
)

print("submissions:", len(submissions))


def choose_best_decision(decision_list):
    if not decision_list:
        return None

    priority_keywords = ["oral", "spotlight", "poster", "accept", "reject"]

    for key in priority_keywords:
        for d in decision_list:
            if d and key in d.lower():
                return d

    return decision_list[0]


def decision_to_status(decision_text):
    if not decision_text:
        return "No Decision"

    d = decision_text.lower()

    if "reject" in d:
        return "reject"
    if "oral" in d:
        return "oral"
    if "spotlight" in d:
        return "spotlight"
    if "poster" in d:
        return "poster"
    if "accept" in d:
        return "poster"

    return decision_text


final_data = []

print("=== decision/rating抽出中 ===")

for note in submissions:
    forum_id = note.id
    content = note.content

    replies = note.details.get("directReplies", [])

    decision_candidates = []
    all_ratings = []

    for rep in replies:
        inv = rep.get("invitation", "")
        rep_content = rep.get("content", {})

        # Decision
        if inv.endswith("/-/Decision"):
            dval = rep_content.get("decision")
            if dval:
                decision_candidates.append(dval)

        # Official Review rating
        if inv.endswith("/-/Official_Review"):
            rating_val = rep_content.get("rating")
            if rating_val:
                try:
                    score = int(str(rating_val).split(":")[0])
                    all_ratings.append(score)
                except:
                    pass

    decision_text = choose_best_decision(decision_candidates)
    status = decision_to_status(decision_text)

    avg_rating = round(statistics.mean(all_ratings), 2) if all_ratings else "N/A"

    final_data.append({
        "番号": note.number,
        "title": content.get("title", ""),
        "status": status,
        "decision_raw": decision_text,
        "rating": avg_rating,
        "all_ratings": all_ratings,
        "authors": ", ".join(content.get("authors", [])),
        "href": f"https://openreview.net/forum?id={forum_id}"
    })

df = pd.DataFrame(final_data)

filename = f"neurips_{YEAR}.csv"
df.to_csv(filename, index=False, encoding="utf-8-sig")

print("完了:", filename)
print(df["status"].value_counts())
print("rating N/A count:", (df["rating"] == "N/A").sum())
