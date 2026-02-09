import pandas as pd
from lxml import html

year = '2013'

def extract_iclr_data(file_path):
    # ファイルを読み込む
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # lxmlで解析する
    tree = html.fromstring(html_content)
    
    # テーブルの行を取得
    rows = tree.xpath('//tbody/tr')
    data = []

    for row in rows:
        cols = row.xpath('.//td')
        
        # データ行でない場合はスキップ
        if not cols or len(cols) < 8:
            continue
            
        # 1. インデックス (列番号 1)
        index = cols[1].text_content().strip()
        
        # 2. Title, OpenReview URL, PDF URL (列番号 2)
        title_cell = cols[2]
        title_link = title_cell.xpath('.//a')
        
        if title_link:
            title = title_link[0].text_content().strip()
            openreview_url = title_link[0].get('href')
        else:
            title = title_cell.text_content().strip()
            openreview_url = ""

        # PDF URLの生成 (OpenReviewのURLがある場合、forumをpdfに置換)
        if openreview_url and 'openreview.net/forum' in openreview_url:
            pdf_url = openreview_url.replace('/forum', '/pdf')
        else:
            pdf_url = ""
            
        # 3. Session/Area (列番号 3)
        session = cols[3].text_content().strip()
        
        # 4. Authors (列番号 4)
        authors = cols[4].text_content().strip()
        
        # 5. Affiliation (列番号 5)
        affiliation = cols[5].text_content().strip()
        
        # 6. Status (列番号 7)
        status = cols[7].text_content().strip()
        
        # データをリストに追加
        data.append({
            'Index': index,
            'Title': title,
            'Session/Area': session,
            'Authors': authors,
            'Affiliation': affiliation,
            'Status': status,
            'OpenReview URL': openreview_url,
            'PDF URL': pdf_url
        })

    return data

# 実行部分
file_path = 'ICLR' + year + '.xml'
extracted_data = extract_iclr_data(file_path)

# DataFrameに変換して表示（または保存）
df = pd.DataFrame(extracted_data)

# 結果の確認
print(f"抽出されたデータ件数: {len(df)}")
print(df.head())

output_file = 'ICLR' + year + '.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')