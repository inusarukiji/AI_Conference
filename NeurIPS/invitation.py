import openreview

client = openreview.Client(baseurl="https://api.openreview.net")

forum_id = "7JqqnRrZfz6"

notes = client.get_notes(forum=forum_id)
print("notes:", len(notes))

for n in notes[:5]:
    print("id:", n.id)
    print("invitation:", n.invitation)
