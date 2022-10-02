# from msilib.schema import Class
# from operator import imod


import unittest
from os import path, getcwd
import ComicDownloader as cd

class TestComicDownloder(unittest.TestCase):

    def test_get_config(self):
        APP_PATH = getcwd()
        CONFIG_FILE_PATH = path.join(APP_PATH, "config.toml")
        conf = cd.get_config(CONFIG_FILE_PATH)
        return self.assertEqual(conf["scraping"]["retry_num"], 3)

if __name__ == "__main__":
    unittest.main()
