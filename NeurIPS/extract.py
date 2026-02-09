import lxml.html
import pandas as pd
import re

def parse_paper_list_to_csv(input_file, output_file):
    # ファイルの読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # HTMLをパース
    tree = lxml.html.fromstring(content)
    
    # テーブルの各行を取得
    rows = tree.xpath('//table[@id="paperlist"]//tbody/tr')
    if not rows:
        # tbodyがない場合のフォールバック
        rows = tree.xpath('//table[@id="paperlist"]//tr')[2:]

    data = []
    for row in rows:
        cols = row.xpath('./td')
        # 必要なカラム数が足りない場合はスキップ
        if len(cols) < 9:
            continue
        
        item = {}
        
        # 1. 番号 (カラム1)
        item['番号'] = cols[1].text_content().strip()
        
        # 2. title (カラム2)
        title_cell = cols[2]
        item['title'] = title_cell.text_content().strip()
        
        # href の抽出用リンク保持
        links = title_cell.xpath('.//a/@href')
        
        # 3. area, 4. authors, 5. affiliation (カラム3, 4, 5)
        item['area'] = cols[3].text_content().strip()
        item['authors'] = cols[4].text_content().strip()
        item['affiliation'] = cols[5].text_content().strip()
        
        # 6. status (カラム7)
        item['status'] = cols[7].text_content().strip()
        
        # 7. rating (カラム8) - タグが含まれる場合の処理
        rating_cell = cols[8]
        rating_val = ""
        
        # data-rating_avg 属性を確認
        rating_span = rating_cell.xpath('.//span[@data-rating_avg]')
        if rating_span:
            raw_rating_attr = rating_span[0].get('data-rating_avg', '')
            # もし属性値に <a>6</a> のようなタグが含まれていたらテキストのみ抽出
            if '<' in raw_rating_attr:
                try:
                    # 文字列を一時的にHTMLとしてパースしてテキストを取得
                    temp_fragment = lxml.html.fromstring(raw_rating_attr)
                    rating_val = temp_fragment.text_content().strip()
                    # rating内のリンクも一応チェック
                    if not links:
                        links = temp_fragment.xpath('.//a/@href')
                except:
                    # パース失敗時は正規表現でタグを除去
                    rating_val = re.sub(r'<[^>]+>', '', raw_rating_attr).strip()
            else:
                rating_val = raw_rating_attr
        else:
            # 属性がない場合はセル内のテキストを直接取得
            rating_val = rating_cell.text_content().strip()
        
        item['rating'] = rating_val

        # 8. href (リンク)
        # タイトルにリンクがなければ、レーティングセル内のリンクを探す
        if not links:
            links = rating_cell.xpath('.//a/@href')
        
        item['href'] = links[0] if links else ""
        
        data.append(item)

    # 指定された順番でデータフレームを作成
    df = pd.DataFrame(data)
    columns_order = ['番号', 'title', 'area', 'authors', 'affiliation', 'status', 'rating', 'href']
    df = df[columns_order]
    
    # CSVに出力 (Excel対応のため utf-8-sig)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"変換が完了しました: {output_file}")
    return df

# --- 実行部分 ---
# ファイル名は適宜変更してください
input_filename = 'neurips2020.xml' 
output_filename = 'papers_data_fixed.csv'

try:
    parse_paper_list_to_csv(input_filename, output_filename)
except Exception as e:
    print(f"エラーが発生しました: {e}")