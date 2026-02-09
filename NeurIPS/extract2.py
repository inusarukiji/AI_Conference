import pandas as pd
from bs4 import BeautifulSoup

YEAR = "2012"

def xml_to_csv(input_file, output_file):
    # ファイルを読み込む
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # BeautifulSoupで解析 (HTML構造が含まれているためhtml.parserを使用)
    soup = BeautifulSoup(content, 'html.parser')
    
    # テーブルの行を取得
    rows = soup.find_all('tr')
    
    data = []
    
    for row in rows:
        cells = row.find_all('td')
        
        # ヘッダー行や空の行をスキップするためのチェック
        # 提供されたデータ構造に基づき、十分な列があるか確認
        if len(cells) < 8:
            continue
            
        try:
            # 1. Index (2番目のtd, インデックス1)
            index = cells[1].get_text(strip=True)
            
            # 2. Title & 6. Link (3番目のtd, インデックス2)
            title_cell = cells[2]
            title_tag = title_cell.find('a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '')
            else:
                title = title_cell.get_text(strip=True)
                link = ''
            
            # 3. Authors (5番目のtd, インデックス4)
            # class="author-link" を持つspanタグから抽出
            author_cell = cells[4]
            authors_list = [span.get_text(strip=True) for span in author_cell.find_all('span', class_='author-link')]
            authors = ", ".join(authors_list)
            
            # 4. Affiliation (6番目のtd, インデックス5)
            # class="aff-link" を持つspanタグから抽出
            aff_cell = cells[5]
            aff_list = [span.get_text(strip=True) for span in aff_cell.find_all('span', class_='aff-link')]
            # 所属がない場合やタグ構造が違う場合のフォールバック
            if not aff_list:
                affiliation = aff_cell.get_text(strip=True)
            else:
                affiliation = "; ".join(aff_list)
            
            # 5. Status (8番目のtd, インデックス7)
            status = cells[7].get_text(strip=True)
            
            # データをリストに追加
            data.append({
                'Index': index,
                'Title': title,
                'Authors': authors,
                'Affiliation': affiliation,
                'Status': status,
                'Link': link
            })
            
        except IndexError:
            continue

    # DataFrameを作成
    df = pd.DataFrame(data)
    
    # CSVとして保存
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"CSVファイルを作成しました: {output_file}")
    print(f"抽出件数: {len(df)}")
    return df

# 実行部分
if __name__ == "__main__":
    input_filename = 'neurips' + YEAR + '.xml'
    output_filename = 'neurips' + YEAR + '.csv'
    
    # 実行
    xml_to_csv(input_filename, output_filename)