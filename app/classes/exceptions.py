####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################


class ZNTSettingTags(Exception):
    def __init__(self, message, detail):
        self.message = message
        self.detail = detail

    def __str__(self):
        return self.message

class ZNTException(Exception):
    pass
