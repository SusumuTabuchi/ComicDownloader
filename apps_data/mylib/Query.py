
# [query]
get_comics_master = "SELECT `id`, `title`, `top_url` FROM `mangas` WHERE magazine IN ({0}) AND `update_flag` = 1"
get_got_items = "SELECT `subtitle` FROM `episodes` WHERE `manga_id` = '{0}'"
insert_get_items = "INSERT INTO `episodes`(`manga_id`, `title`, `subtitle`) VALUES {0}"
