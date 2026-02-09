import openreview
import pandas as pd
import statistics
import sys

client = openreview.api.OpenReviewClient(baseurl="https://api2.openreview.net")

# =========================
# YEAR をターミナル引数から取得
# =========================
if len(sys.argv) < 2:
    print("使い方: python3 gemini_api.py 2024")
    sys.exit(1)

YEAR = sys.argv[1]

CONF = f"NeurIPS.cc/{YEAR}/Conference"
SUBMISSION_INV = f"{CONF}/-/Submission"

print("YEAR:", YEAR)
print("=== submissions (directReplies付き) 取得中 ===")

submissions = client.get_all_notes(
    invitation=SUBMISSION_INV,
    details="directReplies"
)

print("submissions:", len(submissions))

def get_invitations(reply):
    if isinstance(reply, dict):
        return reply.get("invitations", [])
    return getattr(reply, "invitations", [])

def get_content(reply):
    if isinstance(reply, dict):
        return reply.get("content", {})
    return getattr(reply, "content", {})

def choose_best_decision(decision_list):
    if not decision_list:
        return None

    priority_keywords = [
        "oral",
        "spotlight",
        "poster",
        "accept",
        "reject"
    ]

    for key in priority_keywords:
        for d in decision_list:
            if d and key in d.lower():
                return d

    return decision_list[0]

def decision_to_status(decision_text):
    if not decision_text:
        return "No Decision"

    d = decision_text.lower()

    if "oral" in d:
        return "oral"
    elif "spotlight" in d:
        return "spotlight"
    elif "poster" in d:
        return "poster"
    elif "reject" in d:
        return "reject"
    elif "accept" in d:
        return "poster"
    else:
        return decision_text

final_data = []

for note in submissions:
    forum_id = note.id
    content = note.content

    replies = note.details.get("directReplies", []) if hasattr(note, "details") else []

    all_ratings = []
    decision_candidates = []

    for rep in replies:
        invs = get_invitations(rep)
        rep_content = get_content(rep)

        # Decision
        if any(inv.endswith("/-/Decision") for inv in invs):
            dval = rep_content.get("decision", {}).get("value")
            if dval:
                decision_candidates.append(dval)

        # Official Review
        if any(inv.endswith("/-/Official_Review") for inv in invs):
            rating_val = rep_content.get("rating", {}).get("value")
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
        "title": content.get("title", {}).get("value", ""),
        "status": status,
        "decision_raw": decision_text,
        "rating": avg_rating,
        "all_ratings": all_ratings,
        "authors": ", ".join(content.get("authors", {}).get("value", [])),
        "href": f"https://openreview.net/forum?id={forum_id}"
    })

df = pd.DataFrame(final_data)

print("df columns:", df.columns.tolist())
print("df rows:", len(df))

if len(df) == 0:
    print("ERROR: submissionsが取れてないのでCSVが空です。invitationが違う可能性が高いです。")
    sys.exit(1)



filename = f"neurips_{YEAR}.csv"
df.to_csv(filename, index=False, encoding="utf-8-sig")

print("完了:", filename)
print(df["status"].value_counts())
print("rating N/A count:", (df["rating"]=="N/A").sum())
