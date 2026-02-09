from bs4 import BeautifulSoup
import pandas as pd

year = '2017'

def extract_iclr_data(file_path):
    # ファイルを読み込む
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # BeautifulSoupで解析する
    soup = BeautifulSoup(html_content, 'html.parser')

    # テーブルのボディ部分を取得
    tbody = soup.find('tbody')
    if not tbody:
        print("テーブルデータが見つかりませんでした。")
        return []

    rows = tbody.find_all('tr')
    data = []

    for row in rows:
        cols = row.find_all('td')
        
        # データ行でない場合（空行など）はスキップ
        if not cols or len(cols) < 8:
            continue
            
        # 1. インデックス (列番号 1)
        # 0番目は隠しカラムのため、1番目を取得
        index = cols[1].get_text(strip=True)
        
        # 2. Title, OpenReview URL, PDF URL (列番号 2)
        title_cell = cols[2]
        
        # Titleの抽出: ソーシャルリンクのクラスを持たない最初のリンクを探す
        title_link = title_cell.find('a', class_=lambda c: c is None or 'wp-block-social-link-anchor' not in c)
        if title_link:
            title = title_link.get_text(strip=True)
        else:
            # リンクがない場合はセル全体のテキスト（ただし余分な文字が含まれる可能性あり）
            title = title_cell.get_text(strip=True)

        # OpenReview URLの抽出 (title="OpenReview"を持つaタグ)
        or_link = title_cell.find('a', title='OpenReview')
        openreview_url = or_link['href'] if or_link else None
        
        # PDF URLの抽出 (title="PDF"を持つaタグ)
        pdf_link = title_cell.find('a', title='PDF')
        pdf_url = pdf_link['href'] if pdf_link else None
        
        # 3. Session/Area (列番号 3)
        session = cols[3].get_text(strip=True)
        
        # 4. Authors (列番号 4)
        authors = cols[4].get_text(strip=True)
        
        # 5. Affiliation (列番号 5)
        affiliation = cols[5].get_text(strip=True)
        
        # 6. Status (列番号 7) ※列番号6はCountryなのでスキップ
        status = cols[7].get_text(strip=True)
        
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