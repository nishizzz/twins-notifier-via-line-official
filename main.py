import time
import twins_scraping as scraping
import send_by_linebot


# HTMLを収集して今月の日別収益をリスト化
# 成功するまで複数回繰り返す
for i in range(2):  # 最大2回実行
    try:
        new_kj_list = scraping.get_new_kj_list() # HTMLを収集

    except ValueError: # リスト化に失敗したとき（大抵、スクレイピングに失敗して要素0のリストになったとき）
        print(f"{i+1}回目のデータ収集に失敗しました。もう一度繰り返します")
        time.sleep(120) # 2分待つ
        
    else:
        print("データ収集に成功しました。")
        
        # 1要素ずつ、LINEへ送るメッセージとして整形して送信
        for kj in new_kj_list:
            text = send_by_linebot.make_text_for_LINE(kj)
            send_by_linebot.send_message(text)
        
        break
        
else:
    print("最大試行回数に達しました。処理を中断します")
    # LINEへ通知を送信
    send_by_linebot.send_message(f"{i+1}回の試行でデータを収集できませんでした")

