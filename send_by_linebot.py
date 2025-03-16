from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import config
from title_dict import title_dict


def make_text_for_LINE(kj):
    """
    LINE送信用にテキストを整形する
    """

    category = list(title_dict)[kj[5]]

    # 送信するテキストを作成
    text = f"【{category}】\n表題: {kj[1]}\n掲載日時: {kj[4]}"

    return text


def send_message(text):
    """
    LINEでメッセージを送信する
    """

    # 環境変数の読み出し
    LINE_CHANNEL_ACCESS_TOKEN = config.LINE_CHANNEL_ACCESS_TOKEN
    LINE_USER_ID = config.LINE_USER_ID

    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

    try:
        for line_user_id in LINE_USER_ID:
            line_bot_api.push_message(line_user_id, TextSendMessage(text=text))
    except LineBotApiError as e:
        print(e.message)
