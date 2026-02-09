from bs4 import BeautifulSoup
import pandas as pd

year = "2013" # 必要に応じて年を変更してください

def extract_cvpr_data(file_path):
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
        index = cols[1].get_text(strip=True)
        
        # 2. Title, Proceeding URL, PDF URL, CVF URL, Arxiv URL (列番号 2)
        title_cell = cols[2]
        
        # タイトルとProceeding URLの抽出
        # タイトルセル内の最初のリンクがProceedingへのリンクになっています
        title_link = title_cell.find('a')
        if title_link:
            title = title_link.get_text(strip=True)
            proceeding_url = title_link.get('href')
        else:
            title = title_cell.get_text(strip=True)
            proceeding_url = None

        # PDF URLの抽出 (title="PDF"を持つaタグ)
        pdf_link = title_cell.find('a', title='PDF')
        pdf_url = pdf_link['href'] if pdf_link else None

        # CVF URLの抽出 (title="CVF"を持つaタグ) [追加]
        cvf_link = title_cell.find('a', title='CVF')
        cvf_url = cvf_link['href'] if cvf_link else None

        # Arxiv URLの抽出 (title="Arxiv"を持つaタグ) [追加]
        arxiv_link = title_cell.find('a', title='Arxiv')
        arxiv_url = arxiv_link['href'] if arxiv_link else None
        
        # 3. Session/Area (列番号 3)
        session = cols[3].get_text(strip=True)
        
        # 4. Authors (列番号 4)
        authors = cols[4].get_text(strip=True)
        
        # 5. Affiliation (列番号 5)
        affiliation = cols[5].get_text(strip=True)
        
        # 6. Country (列番号 6)
        country = cols[6].get_text(strip=True)

        # 7. Status (列番号 7)
        status = cols[7].get_text(strip=True)
        
        # データをリストに追加
        data.append({
            'Index': index,
            'Title': title,
            'Session/Area': session,
            'Authors': authors,
            'Affiliation': affiliation,
            'Country': country,
            'Status': status,
            'Proceeding URL': proceeding_url,
            'PDF URL': pdf_url,
            'CVF URL': cvf_url,       # [追加]
            'Arxiv URL': arxiv_url    # [追加]
        })

    return data


# 実行部分
file_path = 'ICCV' + year + '.xml'
extracted_data = extract_cvpr_data(file_path)

# DataFrameに変換して表示（または保存）
df = pd.DataFrame(extracted_data)

# 結果の確認
print(f"抽出されたデータ件数: {len(df)}")
print(df.head())

output_file = 'ICCV' + year + '.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')