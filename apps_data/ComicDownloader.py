from argparse import ArgumentError
# from pkgutil import get_loader
import requests
from bs4 import BeautifulSoup as bs
import cv2
# import numpy as np
from pathlib import Path
from PIL import Image
import json

# from operator import mod
# from sre_constants import SUCCESS
import toml
from logging import exception, getLogger, StreamHandler, FileHandler, DEBUG, INFO, WARN, Formatter
import time
import datetime
import re
from os import path, getcwd
# import NewError
from mylib import Message as ms, MariadbClient as mdc, Common as cmn, NewError, Query

# const
APP_PATH = getcwd()
CONFIG_FILE_PATH = path.join(APP_PATH, "config.toml")
STR_ALL = "ALL"
SAVE_DIRECTORY = path.join(APP_PATH, "comics")
HEADERS = {"Referer": "https://shonenjumpplus.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
            }
# Jump+ scraping
READ_MORE_NUM = 150 # 読み込み件数（これ以上はエラー）
NUMBER_SINCE = 10000 # 適当に大きい数字
NUMBER_UNTIL = 0 # 最初の話数　0=1話
ADIMAGE_BASE_URL = "https://cdn-ak-img.shonenjumpplus.com/public/link-slot-series"
ORIGINAL_MIX_IMAGE_PATH = path.join(APP_PATH, "img/tmp/original.png")
# 裏サンデー scraping
URL_TOP_DOMAIN = "https://urasunday.com"
# 話数用 Jump+
PATTERN = '\[(.*)\].*'
RE_MATCH = re.compile(r'{0}'.format(PATTERN))
# 話数用 裏サンデー
US_PATTERN = 'src: \'(.*)\','
US_RE_MATCH = re.compile(r'{0}'.format(US_PATTERN))
# logger
logger = getLogger()

class ComicDownloader:


    def __init__(self, mode="new", select_magazine=STR_ALL, mid=None, mtitle=None, mepisode=None):
        logger.info("Start initialize.")
        self.start_time = []
        self.start_time.append(time.time())

        ### args
        self.magazine = select_magazine
        if mode.lower() in ("new".lower(), "n".lower()):
            self.mode = "new"
        elif mode.lower() in ("full".lower(), "f".lower()):
            self.mode = "full"
        else:
            logger.warning("mode:引数の値が不正です。使用可能な値は'new','full'です")
            raise ArgumentError("mode", "Possible values are 'new' or 'full'")
        # この辺は今は使用しない
        self.target_manga_id = mid
        self.target_manga_title = mtitle
        self.targer_manga_episode = mepisode

        ### config load
        self.config = get_config(CONFIG_FILE_PATH)

        ### DB master
        self.mariadb_client = mdc.MarriadbClient(**self.config["db"])
        self.mariadb_client.connect()
        self.mariadb_client.set_cousor()

        ### DBからデータ取得
        # 更新対象
        self.updates = {
                    "ids": [],
                    "titles": [],
                    "top_urls": []
                }
        # DBに格納の取得済み話数
        self.got_items = {
            "items": []
        }
        self._get_comic_master()
        self._get_got_items()

        # 取得した漫画情報を格納
        self.insert_to_db = []

        # 保存先titleフォルダを全て作成する
        self.create_comic_directory()

        logger.info("End initialize. time: {0}".format(time.time() - self.start_time.pop()))

    def __del__(self):
        del self.mariadb_client

    def _get_comic_master(self):
        if self.magazine == STR_ALL:
            magazine = ",".join([ '"{0}"'.format(s) for s in self.config["comic"]["magazines"]])
        else:
            magazine = '"{0}"'.format(self.magazine)
        query = Query.get_comics_master.format(magazine)
        self.mariadb_client.exec_query(query)
        for target in self.mariadb_client.result:
            id, title, top_url = target.values()
            self.updates["ids"].append(id)
            self.updates["titles"].append(title)
            self.updates["top_urls"].append(top_url)

    def _get_got_items(self):
        for i in range(len(self.updates["ids"])):
            query = Query.get_got_items.format(self.updates["ids"][i])
            self.mariadb_client.exec_query(query)
            self.got_items["items"].append([sub for item in self.mariadb_client.result for _, sub in item.items()])

    def create_comic_directory(self):
        for title in self.updates["titles"]:
            cmn.make_directory(path.join(SAVE_DIRECTORY, title))

    def remade_image(self, source_path, destination_path):

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
        # 切り出しの数値設定
        # weight - rp の値が4で割り切れるような数値でなければならないことに注意する
        # height - bp の値が4で割り切れるような数値でなければならないことに注意する
        # 20230930 bpが0となるパターン出現に伴い、bpの値を指定する
        rp = 28
        bp = 16
        if weight == 764:
            rp = 28
        elif weight == 760:
            rp = 24
        elif weight == 779:
            rp = 11
        elif weight == 822:
            rp = 22
        elif weight == 836:
            rp = 4
        elif weight == 844:
            rp = 12
        elif weight == 841:
            rp = 9
        elif weight == 682:
            rp = 10
        elif weight == 840:
            rp = 8
        elif weight == 967:
            rp = 7
            bp = 24
        elif weight == 1303:
            rp = 23
            bp = 0
        elif weight == 1304:
            rp = 24
            bp = 0
        elif weight == 1440:
            rp = 0
            bp = 0
        else:
            # 想定外のweghitの場合エラー送出
            raise NewError.NewSizeError("New Size Error. weight is [{0}].".format(weight))
        RIGHT_PIXEL = rp # 右からのピクセル数
        BOTTOM_PIXEL = bp # 下からのピクセル数
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

    def get_page_source_to_soup(self, url, headers):
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            soup = bs(r.text, "html.parser")
        elif r.status_code == 503:
            # メンテ中とみなす
            soup = None
        else:
            soup = None
        return soup

    def get_episode_urls_jumpplus(self, soup, url_base):
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
            elif r_api.status_code == 404:
                logger.error("404 Error. When get next episode url. Please check this title. {0}".format(html_json["episode"]["series_title"]))
                break

        return episode_urls, episode_subtitles, episode_is_free

    def get_episode_images_jumpplus(self, episode_urls, episode_subtitles, episode_is_free, count_num):
        # 1話ごとにループして画像を取得する
        for num in range(len(episode_urls)):
            try:
                # 無料の話数でなければスキップ
                if not episode_is_free[num]:
                    logger.debug("Pass because it's not free. title: {0}. subtitle: {1}.".format(self.updates["titles"][count_num], episode_subtitles[num]))
                    continue
                # 取得済みならスキップ
                if episode_subtitles[num] in self.got_items["items"][count_num]:
                    logger.debug("Pass because it has already been obtained. title: {0}. subtitle: {1}.".format(self.updates["titles"][count_num], episode_subtitles[num]))
                    continue
                # 話数フォルダを作成
                destination_dir = path.join(SAVE_DIRECTORY, self.updates["titles"][count_num], episode_subtitles[num])
                cmn.make_directory(destination_dir)

                # 話数ページソースを取得
                episode_url = episode_urls[num]
                retry_count = 0
                while config["scraping"]["retry_num"] >= retry_count:
                    try:
                        r_epi = requests.get(url=episode_url, headers=HEADERS)
                    except Exception as e:
                        logger.debug("title: {0}. subtitle: {1}. message: {2}".format(self.updates["titles"][count_num], episode_subtitles[num], e))
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
                            st_time = time.time()
                            r_random_img = requests.get(random_url)
                            fi_time = time.time() - st_time
                            if fi_time > 2: # 2秒以上掛かったら画像取得エラーとみなす
                                raise Exception("Image acquisition takes too long.{0}ms".format(str(fi_time)))
                        except Exception as e:
                            logger.debug("title: {0}. subtitle: {1}. message: {2}".format(self.updates["titles"][count_num], episode_subtitles[num], e))
                            time.sleep(10)
                            retry_count += 1
                        else:
                            break
                    if r_random_img.status_code == 200:
                        with open(ORIGINAL_MIX_IMAGE_PATH, "wb") as f:
                            f.write(r_random_img.content)
                    # 復元して保存
                    path.join(SAVE_DIRECTORY, self.updates["titles"][count_num], episode_subtitles[num], str(number).zfill(3))
                    if self.remade_image(ORIGINAL_MIX_IMAGE_PATH, path.join(destination_dir, "{0}.png".format(str(number).zfill(3)))):
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
                logger.warning("title: {0}. subtitle: {1}. message: {2}".format(self.updates["titles"][count_num], episode_subtitles[num], e))
                time.sleep(1)
            else:
                logger.info("got: {0} {1}".format(self.updates["titles"][count_num], episode_subtitles[num]))
                self.insert_to_db.append((self.updates["ids"][count_num], self.updates["titles"][count_num], episode_subtitles[num]))
                time.sleep(1)
            finally:
                pass

    def get_episode_urls_urasunday(self, soup):
        # エピソードの情報を取得
        episode_urls = []
        episode_subtitles = []
        episode_is_free = []
        for obj in soup.find_all('li'):
            tmp_subtitles = []
            # 未公開判定
            is_free = True
            if "続きはマンガワンでお楽しみいただけます" in obj.get_text():
                is_free = False
            for obj2 in obj.find_all("a"):
                if len(obj2.find_all("div")) != 0:
                    episode_urls.append(URL_TOP_DOMAIN + obj2.get("href"))
                    for t in obj2.find_all("div"):
                        tmp_subtitles.append(t.get_text())
                    episode_subtitles.append(tmp_subtitles[-3]) # 最後から3番目の要素にサブタイトル（話数）
                    episode_is_free.append(is_free)

        return episode_urls, episode_subtitles, episode_is_free

    def get_episode_images_urasunday(self, episode_urls, episode_subtitles, episode_is_free, count_num):
        get_episode_count = 0
        for num in range(len(episode_urls)):
            try:
                # 無料の話数でなければスキップ
                if not episode_is_free[num]:
                    logger.debug("Pass because it's not free. title: {0}. subtitle: {1}.".format(self.updates["titles"][count_num], episode_subtitles[num]))
                    continue
                # 取得済みならスキップ
                if episode_subtitles[num] in self.got_items["items"][count_num]:
                    logger.debug("Pass because it has already been obtained. title: {0}. subtitle: {1}.".format(self.updates["titles"][count_num], episode_subtitles[num]))
                    continue
                soup = self.get_page_source_to_soup(episode_urls[num], HEADERS)
                # 画像URLを取得
                for obj in soup.find_all('script'):
                    match = US_RE_MATCH.findall(obj.get_text())
                    if match:
                        break

                # 話数フォルダを作成
                destination_dir = path.join(SAVE_DIRECTORY, self.updates["titles"][count_num], episode_subtitles[num])
                cmn.make_directory(destination_dir)

                # 画像をすべて保存
                number = 1
                for img_url in match:
                    # 画像が破損している場合があるのでリトライ実装
                    retry_count = 0
                    while config["scraping"]["retry_num"] >= retry_count:
                        image_path = path.join(destination_dir, "{0}.png".format(str(number).zfill(3)))
                        r_img = requests.get(img_url)
                        if r_img.status_code == 200:
                            with open(image_path, "wb") as f:
                                f.write(r_img.content)
                        if not is_problem_image(image_path):
                            break
                        time.sleep(2)
                        retry_count += 1
                        if config["scraping"]["retry_num"] >= retry_count:
                            logger.info("Retry image acquisition. {0} times. {1}".format(retry_count, image_path))
                        else:
                            logger.warning("Failed to get image. {0}".format(image_path))
                    time.sleep(0.5)
                    number += 1
            except Exception as e:
                logger.warning("title: {0}. subtitle: {1}. message: {2}".format(self.updates["titles"][count_num], episode_subtitles[num], e))
                time.sleep(1)
            else:
                logger.info("got: {0} {1}".format(self.updates["titles"][count_num], episode_subtitles[num]))
                self.insert_to_db.append((self.updates["ids"][count_num], self.updates["titles"][count_num], episode_subtitles[num]))
                time.sleep(1)
            finally:
                pass
        time.sleep(1)

    def update_got_items(self):
        # 取得した話数をDBに挿入
        try:
            self.mariadb_client.start_transaction()
            query = Query.insert_get_items.format(",".join(map(str, self.insert_to_db)))
            self.mariadb_client.exec_query(query)
        except Exception as e:
            logger.warning(ms.QueryError)
            logger.warning(e)
            self.mariadb_client.connection.rollback()
            logger.info(ms.Rollback)
        else:
            try:
                logger.info("\r\n".join(map(str, self.insert_to_db)))
            finally:
                pass
            logger.info("{0} 件DBに挿入しました。".format(str(len(self.insert_to_db))))
        finally:
            self.mariadb_client.commit()

def get_config(config_file_path):
    return toml.load(open(config_file_path))

def is_problem_image(image_path):
    try:
        image_file = Path(image_path)
        with image_file.open('rb') as f:
            # PIL で画像データを開きます。
            # PIL が『画像形式を判定できなかった場合』は、
            # UnidentifiedImageError の例外が発生しました。
            im = Image.open(f, 'r')
            # 画像データの破損をチェックします。
            # ベリファイに失敗した場合は、
            # SyntaxError などの例外が発生しました。
            im.verify()
    except:
        is_problem = True
    else:
        is_problem = False
    return is_problem


if __name__ == "__main__":
    # config
    config = get_config(CONFIG_FILE_PATH)
    ### logger setting
    # handler:console handler2:file
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    filename = config["logger"]["filename"].format('{:%Y%m%d%H}'.format(today))
    handler = StreamHandler()
    handler.setLevel(config["logger"]["setlevel"])
    handler.setFormatter(Formatter(config["logger"]["format"], config["logger"]["date_format"]))
    handler2 = FileHandler(filename=filename)
    handler2.setLevel(config["logger"]["setlevel_filehandler"])
    handler2.setFormatter(Formatter(config["logger"]["format"], config["logger"]["date_format"]))
    logger.setLevel(config["logger"]["setlevel"])
    logger.addHandler(handler)
    logger.addHandler(handler2)
    logger.propagate = False

    logger.info(ms.ApplicationStart)

    # cd = ComicDownloader(mode="full", select_magazine=config["comic"]["magazines"][1]) # jump:0 urasunday: 1 Null:ALL
    cd = ComicDownloader(mode="full")

    for i in range(len(cd.updates["top_urls"])):
        soup = cd.get_page_source_to_soup(cd.updates["top_urls"][i], HEADERS)
        if cd.updates["ids"][i].startswith("jp"):
            a,b,c = cd.get_episode_urls_jumpplus(soup, cd.updates["top_urls"][i])
            cd.get_episode_images_jumpplus(a, b, c, i)
        elif cd.updates["ids"][i].startswith("us"):
            a,b,c = cd.get_episode_urls_urasunday(soup)
            cd.get_episode_images_urasunday(a, b, c, i)

    if len(cd.insert_to_db) > 0:
        cd.update_got_items()
    else:
        logger.info("Number of Updates 0.")

    del cd
    logger.info(ms.ApplicationEnd)
