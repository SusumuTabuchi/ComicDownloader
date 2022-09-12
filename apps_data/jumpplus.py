import requests
from bs4 import BeautifulSoup as bs
import cv2
# import numpy as np
# from PIL import Image
import json

# from operator import mod
# from sre_constants import SUCCESS
import toml
from logging import exception, getLogger, StreamHandler, FileHandler, DEBUG, INFO, WARN, Formatter
import sql
import time
import datetime
import re
import common
from os import path, getcwd
import NewError

def remade_image(source_path, destination_path):

    # 右の細い部分を切り出し
    # 　　右からのピクセル数「28」
    # 下の細い部分を切り出し
    # 　　下からのピクセル数「16」
    # 残りのバラバラ部分を縦横4等分で分割する
    # 分割した画像を左上から下に向かって番号を振り以下のように並び替える
    # 　１　２　３　４
    # 　５　６　７　８
    # 　９　10　11　12
    # 　13　14　15　16
    # 下に結合させる
    # 右に結合させる

    # 変数
    remade_img = None # 最終的に出力する画像
    tmp_img = None # 途中経過の画像

    # 元画像の読み込み
    img_original = cv2.imread(source_path, cv2.IMREAD_COLOR)
    # 画像切り出し [元画像 -> 左：右]
    hight, weight = img_original.shape[:2]

    # 定数
    # 764 x 1200 の場合 ->
    #     836 x 1200 パターンがあることが判明。要修正-> 836 x 1200 の場合はRIGHT_PIXEL = 4
    #     822 x 1200 パターンもある・・・ -> RIGHT_PIXEL = 22
    # 20220901 - 修正 元画像weightの値によってRIGHT_PIXELを変更する
    if weight == 764:
        rp = 28
    elif weight == 760:
        rp = 24
    elif weight == 822:
        rp = 22
    elif weight == 836:
        rp = 4
    elif weight == 844:
        rp = 12
    else:
        rp = 28
        raise NewError.NewSizeError(weight)
    RIGHT_PIXEL = rp # 右からのピクセル数
    BOTTOM_PIXEL = 16 # 下からのピクセル数
    SPLIT_X = 4 # 横分割数
    SPLIT_Y = 4 # 縦分割数

    # img[top : bottom, left : right]
    img_right = img_original[0 : hight, weight - RIGHT_PIXEL: weight]
    img_left = img_original[0 : hight, 0: weight - RIGHT_PIXEL]

    # 画像切り出し [左 -> 左上：下]
    hight, weight = img_left.shape[:2]
    # img[top : bottom, left : right]
    img_random = img_left[0 : hight - BOTTOM_PIXEL, 0: weight]
    img_down = img_left[hight - BOTTOM_PIXEL : hight, 0: weight]

    # 画像切り出し [左上 -> 左上]
    hight, weight = img_random.shape[:2]
    # [左上を分割して並び替え]
    cx = 0
    cy = 0
    for j in range(SPLIT_X):
        for i in range(SPLIT_Y):
            split_pic = img_random[cy: cy + int(hight / SPLIT_Y), cx: cx + int(weight / SPLIT_X), : ]
            if i == 0:
                tmp_img = split_pic
            else:
                tmp_img = cv2.hconcat([tmp_img, split_pic]) # 横に連結
                if i == 3:
                    if j == 0:
                        remade_img = tmp_img
                    else:
                        remade_img = cv2.vconcat([remade_img, tmp_img]) # 縦に連結
            cy = cy + int(hight / SPLIT_Y)
        cy = 0
        cx = cx + int(weight / SPLIT_X)

    # 結合させる [左上 + 左下 -> 左]
    remade_img = cv2.vconcat([remade_img, img_down]) # 縦に連結
    # 結合させる [左 ＋ 右 -> 完成]
    remade_img = cv2.hconcat([remade_img, img_right]) # 縦に連結
    # 画像を保存する 成功でTrue、失敗でFalse
    return cv2.imwrite(destination_path, remade_img)


if __name__ == "__main__":
    ### いずれ引数に 漫画や話数を指定して取得する
    m_id = None # manga_id
    m_title = None # manga_title
    m_top_url = None # manga_top_url
    specify_target = m_id is not None or m_title is not None or m_top_url is not None # 更新対象の漫画を指定する

    ### 定数
    ADIMAGE_BASE_URL = "https://cdn-ak-img.shonenjumpplus.com/public/link-slot-series"
    ORIGINAL_MIX_IMAGE_PATH = "img/tmp/original.png"
    MAGAZINE = "少年ジャンプ+"
    SAVE_DIRECTORY = path.join(getcwd(), "comics")
    HEADERS = {"Referer": "https://shonenjumpplus.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
                }
    # 話数用
    PATTERN = '\[(.*)\].*'
    RE_MATCH = re.compile(r'{0}'.format(PATTERN))
    # scraping
    READ_MORE_NUM = 150 # 読み込み件数（これ以上はエラー）
    NUMBER_SINCE = 10000 # 適当に大きい数字
    NUMBER_UNTIL = 0 # 最初の話数　0=1話

    ### config load
    config = toml.load(open("config.toml"))
    str_const = toml.load(open("const.toml"))

    ### logger
    # handler:console handler2:file
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    filename = config["logger"]["filename"].format('{:%Y%m%d}'.format(today))
    handler = StreamHandler()
    handler.setLevel(config["logger"]["setlevel"])
    handler.setFormatter(Formatter(config["logger"]["format"]))
    handler2 = FileHandler(filename=filename)
    handler2.setLevel(config["logger"]["setlevel_filehandler"])
    handler2.setFormatter(Formatter(config["logger"]["format"]))
    logger = getLogger(__name__)
    logger.setLevel(config["logger"]["setlevel"])
    logger.addHandler(handler)
    logger.addHandler(handler2)
    logger.propagate = False

    logger.info(str_const["application"]["ApplicationStart"])

    # 更新対象一覧を取得
    updates = {
                "ids": [],
                "titles": [],
                "top_urls": []
            }
    got_items = {
        "items": []
    }
    insert_to_db = [] # 取得した漫画情報を格納しておく
    if specify_target:
        try:
            start_block = time.time()

            updates["ids"].append("jp0002")
            updates["titles"].append("君のことが大大大大大好きな100人の彼女")
            updates["top_urls"].append("https://shonenjumpplus.com/episode/13933686331623812157")
            # mariadb client
            mdc = sql.MarriadbClient(**config["db"], logger=logger)
            mdc.connect()
            mdc.set_cousor()
            # 取得済みの話数データ
            for i in range(len(updates["ids"])):
                query = str_const["query"]["get_got_items"].format(updates["ids"][i])
                mdc.exec_query(query)
                got_items["items"].append([sub for item in mdc.result for _, sub in item.items()])
        except:
            logger.warn("更新対象データを取得できませんでした。")
        else:
            logger.info("更新対象は {0} 件です。".format(len(updates["ids"])))
            logger.debug("更新対象：{0}".format([title for title in updates["titles"]]))
        finally:
            # 初期化して解放
            del mdc
            end_block = time.time()
            logger.debug("[get update target] block time: {0}".format(end_block - start_block ))
    else:
        try:
            start_block = time.time()
            # mariadb client
            mdc = sql.MarriadbClient(**config["db"], logger=logger)
            mdc.connect()
            mdc.set_cousor()

            query = str_const["query"]["get_comics"].format(MAGAZINE)
            mdc.exec_query(query)
            # スクレイピング用データ
            for target in mdc.result:
                id, title, top_url = target.values()
                updates["ids"].append(id)
                updates["titles"].append(title)
                updates["top_urls"].append(top_url)
            # 取得済みの話数データ
            for i in range(len(updates["ids"])):
                query = str_const["query"]["get_got_items"].format(updates["ids"][i])
                mdc.exec_query(query)
                got_items["items"].append([sub for item in mdc.result for _, sub in item.items()])
        except:
            logger.warn("更新対象データを取得できませんでした。")
        else:
            logger.info("更新対象は {0} 件です。".format(len(updates["ids"])))
            logger.debug("更新対象：{0}".format([title for title in updates["titles"]]))
        finally:
            # 初期化して解放
            del mdc
            end_block = time.time()
            logger.debug("[get update target] block time: {0}".format(end_block - start_block ))

    # 保存先titleフォルダを全て作成する
    for title in updates["titles"]:
        common.make_directory(path.join(SAVE_DIRECTORY, title))


    for i in range(len(updates["top_urls"])):
        start_block = time.time()
        logger.debug("ready: {0}".format(updates["titles"][i]))
        # titleのtopURL
        url_base = updates["top_urls"][i]
        # ページソースを取得する
        r = requests.get(url=url_base, headers=HEADERS)
        if r.status_code == 200:
            soup = bs(r.text, "html.parser")
        elif r.status_code == 503:
            # メンテ中とみなす
            logger.warn(str_const["scraping"]["Is_maintenance"].format(title))
            break

        # 固定値を取得
        for html in soup.find_all('html'):
            if html.get('data-gtm-data-layer') is not None:
                html_json = json.loads(html.get('data-gtm-data-layer')) #json形式に変換する
                # 最初の1個でbreak
                break
        series_id = html_json["episode"]["series_id"] # title毎の固定値

        # 全ての話数データを取得する
        # 隠れている話数を取得するAPI
        next_api_url = "https://shonenjumpplus.com/api/viewer/readable_products?aggregate_id={0}&number_since={1}&number_until={2}&read_more_num={3}&type=episode".format(series_id, NUMBER_SINCE, NUMBER_UNTIL, READ_MORE_NUM)
        # エピソードの情報を取得
        episode_urls = []
        episode_subtitles = []
        episode_is_free = []
        while True:
            api_url = next_api_url
            r_api = requests.get(url=api_url, headers=HEADERS)
            if r_api.status_code == 200:
                api_data = json.loads(r_api.text)

            next_api_url = api_data["nextUrl"]

            api_soup = bs(api_data["html"],"html.parser")

            counter = 1
            for obj in api_soup.find_all("li"):
                free = False
                for li in obj.find_all("a"):
                    episode_urls.append(li.get("href"))
                for li in obj.find_all("h4"):
                    episode_subtitles.append(RE_MATCH.match(li.get_text()).groups()[0]) # 正規表現で話数だけ取得
                for li in obj.find_all("span"):
                    if li.get_text() == "無料":
                        free = True
                episode_is_free.append(free)
                counter += 1
            # ループ停止条件：
            # 1.取得したデータがREAD_MORE_NUM未満
            # 2.取得したデータがREAD_MORE_NUMと一致 かつ 最後の一つのURLがurl_baseと一致
            if counter < READ_MORE_NUM or (counter == READ_MORE_NUM and episode_urls[-1] == url_base):
                break
            time.sleep(1)

        # 1話ごとにループして画像を取得する
        get_episode_count = 0
        for num in range(len(episode_urls)):
            try:
                logger.debug(episode_subtitles[num])
                # 無料の話数でなければスキップ
                if not episode_is_free[num]:
                    continue
                # 取得済みならスキップ
                if episode_subtitles[num] in got_items["items"][i]:
                    continue
                # 話数フォルダを作成
                destination_dir = path.join(SAVE_DIRECTORY,updates["titles"][i], episode_subtitles[num])
                common.make_directory(destination_dir)

                # 話数ページソースを取得
                episode_url = episode_urls[num]
                retry_count = 0
                while config["scraping"]["retry_num"] >= retry_count:
                    try:
                        r_epi = requests.get(url=episode_url, headers=HEADERS)
                    except Exception as e:
                        logger.debug("title: {0}. subtitle: {1}. message: {2}".format(updates["titles"][i], episode_subtitles[num], e))
                        time.sleep(10)
                        retry_count += 1
                    else:
                        break
                if r_epi.status_code == 200:
                    epi_soup = bs(r_epi.text, "html.parser")

                # ページトップの広告？画像　※バラバラになってないのでそのまま保存可能
                img_urls = []
                #全てのimgタグをループ処理し、data-srcを出力する
                for img in epi_soup.find_all("img"):
                    # print(img.get('data-src'))
                    if img.get("data-src") is not None and img.get("data-src").startswith(ADIMAGE_BASE_URL):
                        img_urls.append(img.get("data-src"))
                del img_urls[-1] # 最後の一枚は不要

                #全てのjsタグをループ処理し、data-valueで指定された値を出力する
                for sc in epi_soup.find_all("script"):
                    if sc.get("data-value") is not None:
                        # json形式に変換
                        sc_data = json.loads(sc.get("data-value"))
                        # 最初の1個でbreak
                        break
                # 画像（バラバラ画像）のURLリストを作成
                random_urls = [page[page_data] for page in sc_data["readableProduct"]["pageStructure"]["pages"] for page_data in page if page_data == "src"]

                # バラバラ画像を復元して保存
                number = 1
                for random_url in random_urls:
                    # 元画像保存
                    retry_count = 0
                    while config["scraping"]["retry_num"] >= retry_count:
                        try:
                            r_random_img = requests.get(random_url)
                        except Exception as e:
                            logger.debug("title: {0}. subtitle: {1}. message: {2}".format(updates["titles"][i], episode_subtitles[num], e))
                            time.sleep(10)
                            retry_count += 1
                        else:
                            break
                    if r_random_img.status_code == 200:
                        with open(ORIGINAL_MIX_IMAGE_PATH, "wb") as f:
                            f.write(r_random_img.content)
                    # 復元して保存
                    path.join(SAVE_DIRECTORY,updates["titles"][i], episode_subtitles[num], str(number).zfill(3))
                    if remade_image(ORIGINAL_MIX_IMAGE_PATH, path.join(destination_dir, "{0}.png".format(str(number).zfill(3)))):
                        number += 1
                    time.sleep(0.5)

                # ページトップの広告？画像を保存
                for img_url in img_urls:
                    r_img = requests.get(img_url)
                    if r_img.status_code == 200:
                        with open(path.join(destination_dir, "{0}.png".format(str(number).zfill(3))), "wb") as f:
                            f.write(r_img.content)
                            number += 1
                    time.sleep(0.5)

            except Exception as e:
                logger.debug("some error.", e)
            else:
                logger.info("got: {0} {1}".format(updates["titles"][i], episode_subtitles[num]))
                insert_to_db.append((updates["ids"][i], updates["titles"][i], episode_subtitles[num]))
                get_episode_count += 1
            finally:
                time.sleep(1)
        end_block = time.time()
        logger.debug("[get target] block time: {0}. title: {1}.".format(end_block - start_block , "tilte: ", updates["titles"][i]))

    # 取得した話数をDBに挿入
    try:
        # mariadb client
        start_block = time.time()
        mdc = sql.MarriadbClient(**config["db"], logger=logger)
        mdc.connect()
        mdc.set_cousor()

        mdc.start_transaction()

        query = str_const["query"]["insert_get_items"].format(",".join(map(str, insert_to_db)))
        mdc.exec_query(query)
    except:
        logger.warning(str_const["db"]["QueryError"])
        logger.warning(e)
        mdc.connection.rollback()
        logger.info(str_const["db"]["Rollback"])
    else:
        logger.info("{0} 件DBに挿入しました。".format(str(len(insert_to_db))))
    finally:
        mdc.commit()
        # 初期化して解放
        del mdc
        end_block = time.time()
        logger.debug("[update db] block time: {0}".format(end_block - start_block ))

    logger.info("{0} 件取得しました。".format(get_episode_count))
    logger.info(str_const["application"]["ApplicationEnd"])


