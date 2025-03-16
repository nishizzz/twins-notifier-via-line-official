import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from datetime import datetime
import config
from title_dict import title_dict


def HTML2datalist(html):
    """
    HTMLから各掲示の情報を抽出してリストに格納する
    """

    soup = BeautifulSoup(html, "html.parser")

    # テーブルの行を取得
    rows = soup.find("table", {"class": "normal"}).find("tbody").find_all("tr")

    data_list = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue  # 列数が足りない場合はスキップ

        # 各列のデータを取得
        col1 = cols[0].get_text(strip=True)  # ジャンル
        a_tag = cols[1].find("a")  # 表題のリンク内テキスト
        col2 = a_tag.get_text(strip=True) if a_tag else cols[1].get_text(strip=True)
        date_parts = list(cols[2].stripped_strings)  # 掲示期間（開始・終了）
        col3, col4 = date_parts if len(date_parts) == 2 else ("", "")
        col5 = cols[3].get_text(strip=True)  # 掲載日時

        # リストに追加
        data_list.append([col1, col2, col3, col4, col5])
    
    return data_list


def cut_out_new_posts(title, data_list):
    """
    与えられた掲示のリストから新規掲示を切り出す
    """

    # last_sent.txt から最後に送信された掲示の掲示時刻をリストとして読み込む
    with open("last_sent.txt", "r") as f:
        last_sent_list = []
        for line in f:
            last_sent_list = line.split(",") if line != "\n" else last_sent_list
    
    # リスト内の場所
    order = title_dict[title]

    # 変換対象の文字列
    last_sent_date_str = last_sent_list[order]

    # 送信する掲示を格納するリスト
    new_posts = []
    
    # 送信済みの掲示がなければ last_sent をひとまず現在の時刻とする(今回は何も送信しない)
    if last_sent_date_str == "":
        last_sent = datetime.now()
    # 過去に送信済みの掲示があるとき
    else:
        # 文字列を datetime 型に変換
        last_sent = datetime.strptime(last_sent_date_str, "%Y/%m/%d %H:%M:%S")

    # data_list の各データについて、掲載日時を last_sent と比較し、last_sent より新しければ new_posts に加える
    for data in data_list:
        date_str = data[4] # 掲載日時
        date = datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S")
        if date > last_sent:
            data_plus_order = data + [order] # 辞書型の中での位置もリスト末尾に加える
            new_posts.append(data_plus_order)
        else:
            break
    
    # last_sent_list を最新の掲示の掲示時刻で更新
    if data_list != []:
        last_sent_list[order] = data_list[0][4]
    else:
        last_sent_list[order] = last_sent.strftime("%Y/%m/%d %H:%M:%S")
    

    # last_sent.txt を更新する
    with open("last_sent.txt", "w+") as f:
        for i in range(len(last_sent_list)):
            if i == 0:
                f.write(last_sent_list[i])
            else:
                f.write("," + last_sent_list[i])
    

    return new_posts


def scrape_TWINS(driver, wait, wait_time, title):
    """
    指定したタイトルの掲示ページに飛び、掲示一覧を取得する
    その後、新規掲示を切り出して返す
    """
    
    if title not in title_dict:
        print(f"「{title}」という名前のタイトルがリストに存在しません。.env-example の例にあるタイトルを指定してください。")
        return []
    else:
        order = title_dict[title]

        # 「掲示」画面を開く
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="tab-kj"]/p')))
        kj_button = driver.find_element(By.XPATH, '//*[@id="tab-kj"]/p')
        time.sleep(wait_time) # 一応ダメ押しで待つ
        kj_button.click()

        # 指定したタイトルの中の「もっと読む」ボタンの表示を待ってクリック
        # すべての「…もっと読む」リンクを取得
        elements = wait.until(EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, "もっと読む")))
        time.sleep(wait_time) # 一応ダメ押しで待つ

        # 指定した番号の要素をクリック（例: 3番目）
        if order < len(elements):
            elements[order].click()
        else:
            print(f"指定した {order + 1} 番目の要素は存在しません")


        # 表が格納されている? iframeの表示を待って切り替える
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        time.sleep(wait_time) # 一応ダメ押しで待つ
        driver.switch_to.frame(iframe) # iframe に切り替え

        # きちんとデータを取得できているのを確認するまでHTML取得を繰り返す
        count = 0
        data_list = []
        while count < 3: # 10秒おきに3回まで施行する
            # テーブルが表示されるまで待つ
            # iframe 内のテーブルが表示されるまで待つ（例として、tableタグで特定）
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            time.sleep(wait_time) # 一応ダメ押しで待つ

            # HTMLの取得
            html = driver.page_source
            
            data_list = HTML2datalist(html) # リスト化

            # data_list が空でないならbreak
            if len(data_list) != 0:
                break

            count += 1
            if count < 3:
                time.sleep(5) # 最後の試行が終わった後は待たない
            if (count == 3) and (len(data_list) == 0):
                """
                この項は raise で書くべき？
                """
                print(f"{title}のデータ取得に失敗しました")
        
        # 元のコンテキストに戻る
        driver.switch_to.default_content()

        return data_list
    

def get_new_kj_list():
    """
    TWINSの「掲示」ページを開き、指定のタイトルの掲示について新規掲示があれば new_kj_list に追加する
    """

    # ログイン情報など、環境変数をconfigから読み込む
    user_id = config.USER_ID
    password = config.PASS
    notify_title_list = config.NOTIFY_TITLE_LIST

    # Seleniumをヘッドレスモードで実行する
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless') # Selenium3まで
    #options.headless = True # Selenium4(なぜか動作しない)

    # WebDriverを起動
    driver = webdriver.Firefox(options=options)

    # あとで待機するときのため
    max_wait = 240
    wait_time = 1
    driver.implicitly_wait(max_wait) # find_element()もしくはfind_elements()を呼んでいるときに限り、見つかるまで一定の時間待機
    wait = WebDriverWait(driver=driver, timeout=max_wait) # 何かが表示されるまで待機する時に使う

    
    try:
        # ログインページにアクセス
        login_url = "https://twins.tsukuba.ac.jp/campusweb/campusportal.do?locale=ja_JP"
        driver.get(login_url)

        # ログインフォームが見つかったら入力
        user_field = driver.find_element(By.NAME, "userName")
        user_field.send_keys(user_id)
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)

        # ログインボタンの表示を待ってクリック
        login_button = driver.find_element(By.XPATH, '//*[@id="LoginFormSlim"]/tbody/tr/td[6]/button/span')
        time.sleep(wait_time) # 一応ダメ押しで待つ
        login_button.click()
        
        # 通知したいタイトルそれぞれについてスクレイピングを実行し、新規掲示はリストに格納
        new_kj_list = []
        for title in notify_title_list:
            # スクレイピング
            data_list = scrape_TWINS(driver, wait, wait_time, title)
            # 新規掲示の切り出し
            new_posts = cut_out_new_posts(title, data_list)

            # 掲載が古い順に並び替えて追加
            new_posts.reverse()
            for new_post in new_posts:
                new_kj_list.append(new_post)

    finally:
        # WebDriverを閉じる
        driver.quit()
    
    """ デバッグ用
    with open("html.txt", "w") as f:
        f.write(html)
    """
    
    return new_kj_list
