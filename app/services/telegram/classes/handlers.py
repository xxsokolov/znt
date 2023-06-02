####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################
import re
import html
import io
import types
import json

from PIL import Image, ImageDraw, ImageFont
from .render_grafana import RenderingPNG
from app import config, logger
from app.classes.exceptions import *


class FailSafeDict(dict):
    def __missing__(self, key):
        return '{{key not found: {}}}'.format(key)


class ZNT:

    def __init__(self, bots, zabbix_req, preferences):
        self.options = preferences.znt.options
        self.macros = preferences.zabbix.macros
        self.send = preferences.telegram.send
        self.logger = logger.log
        self.zabbix_req = zabbix_req
        self.chart_name: str
        self.chart_period: int
        self.links: list = []
        self.tags: list = []
        self.zntsettings: dict = {}
        self.settings_not_notify: bool = False
        self.settings_chart_disable: bool = False
        self.settings_chart_single: bool = False
        self.settings_chart_group: bool = False
        self.mentions: list = []
        self.chart_png: list = []
        self.message: str
        self.bot_list: list = bots
        self.bot_name: str
        self.bot_token: str
        self.bot_proxy_use: bool
        self.bot_proxy: types.SimpleNamespace
        self.__create_settings_list()
        self.__handling_settings()
        self.__init_bot()

        self.__settings_chart_period()
        self.__create_graph_name()
        self.__create_links()
        self.__create_tags()
        self.__create_mentions_list()
        self.__create_chart()
        if any(True if x else False for x in self.chart_png):
            self.__watermark_text()
        self.__create_message()

    def __create_message(self):
        message_header = html.escape(
            self.send.message.header.format_map(FailSafeDict(json.loads(config.get('znt.settings', 'emoji_map')))))
        if config.get('znt.settings', 'body_messages_cut_symbol') and len(self.send.message.body) > int(
                config.get('znt.settings', 'body_messages_max_symbol')):
            truncated = True
            self.logger.info(
                "Message truncated to {} characters".format(config.get('znt.settings', 'body_messages_max_symbol')))
        else:
            truncated = False
        body = '{} <a href="{}">...</a>'.format(
            html.escape(self.send.message.body)[:config.get('znt.settings', 'body_messages_max_symbol')],
            config.get('zabbix', 'event_url').format(
                zabbix_server=config.get('zabbix', 'url'), eventid=self.macros.eventid,
                triggerid=self.macros.triggerid)) if truncated else html.escape(self.send.message.body)

        links = ' '.join(self.links) if config.get('znt.settings', 'body_messages_url') and len(self.links) != 0 else ''

        tags = ' '.join(self.tags) if config.get('znt.settings', 'body_messages_tags') and len(self.tags) != 0 else ''

        tags_settings = ' '.join(self.zntsettings['tags']) if config.get('znt.settings', 'body_messages_tags') and len(
            self.zntsettings['tags']) != 0 else ''

        mentions = ' '.join(self.mentions) if not isinstance(self.mentions, bool) and config.get(
            'znt.settings', 'body_messages_mentions_settings') and len(
            self.mentions) != 0 else ''

        self.message = config.get('znt.settings', 'body_messages').format(
            subject=message_header, body='\n\n' + body if body else '', links='\n' + links if links else '',
            tags='\n\n' + tags if tags else '', tags_settings='\n\n' + tags_settings if tags_settings else '',
            mentions='\n\n' + mentions if mentions else '')
        return

    def __watermark_text(self):
        try:
            new_chart_png = []
            for chart in self.chart_png:

                img = io.BytesIO(chart)
                img = Image.open(img).convert("RGBA")

                if img.height < int(config.get('znt.settings', 'watermark_minimal_height')):
                    self.logger.info(
                        "Cannot set watermark text, img height {} (min. {})".format(
                            img.height, config.get('znt.settings', 'watermark_minimal_height')))
                    return False

                font = ImageFont.load_default()
                line_width, line_height = font.getsize(config.get('znt.settings', 'watermark_label'))

                txt = Image.new('RGBA', (line_width, line_height))

                from ast import literal_eval
                ImageDraw.Draw(txt).text((0, 0), config.get('znt.settings', 'watermark_label'),
                                         fill=literal_eval(config.get('znt.settings', 'watermark_fill')), font=font)

                txt = txt.rotate(int(config.get('znt.settings', 'watermark_rotate')), resample=Image.BICUBIC,
                                 expand=True)

                img_size = img.crop().size
                size = (img_size[0] - txt.size[0] - 10, img_size[1] - txt.size[1] - 5)
                img.paste(literal_eval(config.get('znt.settings', 'watermark_text_color')), box=size, mask=txt)

                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                new_chart_png.append(img_byte_arr)
            self.chart_png.clear()
            self.chart_png = new_chart_png
        except Exception as err:
            self.logger.error("Exception occurred: {}".format(err), exc_info=config.get('logging', 'exc_info'))
            raise err
        else:
            return

    def __create_chart(self):
        if (self.options.graphs and config.get('znt.settings', 'zabbix_graph')) and not self.settings_chart_disable:

            settings_dash = next((x for x in self.zntsettings[config.get('znt.settings', 'trigger_settings_tag')] if
                                  config.get('znt.settings', 'trigger_settings_tag_grafana_dash') in x), None)
            if settings_dash:
                uid = None
                panel = None
                # Добавляем рендер дашборда Графаны
                if re.findall(r"&", settings_dash):
                    params = settings_dash.split('&')
                    for x in params:
                        if re.findall(config.get('znt.settings', 'trigger_settings_tag_grafana_dash'), x):
                            uid = x.split('=')[1]
                            if not uid:
                                self.logger.warn('В теге "{}" пустой параметр "{}".'.format(
                                    settings_dash, config.get('znt.settings', 'trigger_settings_tag_grafana_dash')))
                        elif re.findall(config.get('znt.settings', 'trigger_settings_tag_grafana_panel'), x):
                            panel = x.split('=')[1]
                            if not panel:
                                self.logger.warn('В теге "{}" пустой параметр "{}".'.format(
                                    settings_dash, config.get('znt.settings', 'trigger_settings_tag_grafana_panel')))
                else:
                    uid = str(settings_dash.split('=')[1])

                if uid and panel:
                    png = RenderingPNG(uid=uid, panel=panel).get_screenshot()
                    if png:
                        self.chart_png.append(png)
                elif uid:
                    png = RenderingPNG(uid=uid).get_screenshot()
                    if png:
                        self.chart_png.append(png)
                else:
                    self.logger.warn(
                        'В теге "{0}" не указан дашборд Grafana. (Прим. {0}YGLp1d14k)'.format(
                            config.get('znt.settings', 'trigger_settings_tag_grafana_dash')))
            # Добавляем графики на основании itemid из экшена
            if self.settings_chart_single:
                item_id = [x for x in self.macros.itemid.split()][0]
                if re.findall(r"\d+", item_id):
                    self.chart_png.append(self.zabbix_req.get_chart_png(itemid=item_id, name=self.chart_name,
                                                                        period=self.chart_period))
            elif self.settings_chart_group:
                for item_id in list(set([x for x in self.macros.itemid.split()])):
                    if re.findall(r"\d+", item_id):
                        self.chart_png.append(self.zabbix_req.get_chart_png(itemid=item_id, name=self.chart_name,
                                                                            period=self.chart_period))

    def __create_links(self):
        # trigger url
        self.links.append(self.__create_links_list(
            _bool=True if self.options.triggerlinks and config.get('znt.settings',
                                                                   'body_messages_url_notes') else False,
            url=self.macros.triggerurl,
            _type=config.get('znt.settings', 'body_messages_url_emoji_notes')))
        # history url
        for item_id in list(set([x for x in self.macros.itemid.split()])):
            if re.findall(r"\d+", item_id):
                items_link = self.__create_links_list(
                    _bool=True if self.options.graphlinks and config.get('znt.settings',
                                                                         'body_messages_url_graphs') else False,
                    url=config.get('zabbix', 'history_url').format(
                        zabbix_server=config.get('zabbix', 'url'),
                        itemid=item_id,
                        range_time=self.options.graphs_period),
                    _type=config.get('znt.settings', 'body_messages_url_emoji_graphs')
                )
                self.links.append(items_link) if items_link else None
        # host url
        self.links.append(self.__create_links_list(
            _bool=True if self.options.hostlinks and config.get('znt.settings', 'body_messages_url_host') else False,
            url=config.get('zabbix', 'host_url').format(zabbix_server=config.get('zabbix', 'url'),
                                                        host=self.macros.hostname),
            _type=config.get('znt.settings', 'body_messages_url_emoji_host')))
        # ack url
        self.links.append(self.__create_links_list(
            _bool=True if self.options.acklinks and config.get('znt.settings', 'body_messages_url_ack') else False,
            url=config.get('zabbix', 'ack_url').format(zabbix_server=config.get('zabbix', 'url'),
                                                       eventid=self.macros.eventid),
            _type=config.get('znt.settings', 'body_messages_url_emoji_ack')))
        # event url
        self.links.append(self.__create_links_list(
            _bool=True if self.options.eventlinks and config.get('znt.settings', 'body_messages_url_event') else False,
            url=config.get('zabbix', 'event_url').format(zabbix_server=config.get('zabbix', 'url'),
                                                         eventid=self.macros.eventid,
                                                         triggerid=self.macros.triggerid),
            _type=config.get('znt.settings', 'body_messages_url_emoji_event')))
        return

    def __create_tags(self):
        # self.__create_tags_list()
        event = self.__create_tags_list(
            _bool=True if self.options.eventtag and config.get('znt.settings', 'body_messages_tags_event') else False,
            tag=self.macros.eventtags, _type=None)
        eventid = self.__create_tags_list(
            _bool=True if self.options.eventtag and config.get('znt.settings', 'body_messages_tags_eventid') else False,
            tag=self.macros.eventid, _type=config.get('znt.settings', 'body_messages_tags_prefix_eventid'))
        itemid = self.__create_tags_list(
            _bool=True if self.options.itemidtag and config.get('znt.settings', 'body_messages_tags_itemid') else False,
            tag=' '.join([item_id for item_id in self.macros.itemid.split() if re.findall(r"\d+", item_id)]),
            _type=config.get('znt.settings', 'body_messages_tags_prefix_itemid'))
        triggerid = self.__create_tags_list(
            _bool=True if self.options.triggeridtag and config.get('znt.settings',
                                                                   'body_messages_tags_triggerid') else False,
            tag=self.macros.triggerid, _type=config.get('znt.settings', 'body_messages_tags_prefix_triggerid'))
        actionid = self.__create_tags_list(
            _bool=True if self.options.actionidtag and config.get('znt.settings',
                                                                  'body_messages_tags_actionid') else False,
            tag=self.macros.actionid, _type=config.get('znt.settings', 'body_messages_tags_prefix_actionid'))
        hostid = self.__create_tags_list(
            _bool=True if self.options.hostidtag and config.get('znt.settings', 'body_messages_tags_hostid') else False,
            tag=self.macros.hostid, _type=config.get('znt.settings', 'body_messages_tags_prefix_hostid'))

        self.tags = [x if x else None for x in [event, eventid, itemid, triggerid, actionid, hostid]]
        return

    # def create_zntsettings(self):
    #     self.zntsettings =
    #     return

    # def create_zntmentions(self):
    #     self.mentions =
    #     return

    def __create_graph_name(self):
        self.chart_name = config.get('znt.settings', 'body_messages_title').format(
            title=self.send.charts.title, period_time=self.__create_graph_period())

    def __create_graph_period(self):
        seconds = int(self.chart_period)
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if days > 0:
            return '{}d {}h'.format(days, hours) if hours > 0 else '{}d'.format(days)
        elif hours > 0:
            return '{}h {}m'.format(hours, minutes) if minutes > 0 else '{}h'.format(hours)
        elif minutes > 0:
            return '{}m'.format(minutes)

    # def create_draw_style(self, settings):
    #     return self.__settings_draw_style(settings)

    def __create_tags_list(self, _bool=False, tag=None, _type=None):
        tags_list = []
        settings_list = []
        try:
            if _bool:
                if tag and (re.search(r'\w', tag)):
                    for tags in tag.split(', '):
                        if tags:
                            if tags.find(':') != -1:
                                tag, value = re.split(r':+', tags, maxsplit=1)
                                if tag != config.get('znt.settings', 'trigger_settings_tag') and tag != config.get(
                                        'znt.settings', 'trigger_info_mentions_tag'):
                                    tags_list.append('#{tag}_{value}'.format(
                                        tag=_type + re.sub(r"\W+", "_", tag) if _type else re.sub(r"\W+", "_", tag),
                                        value=re.sub(r"\W+", "_", value)))
                                else:
                                    continue
                            else:
                                if len(tags.split()) > 0:
                                    for tg_s in tags.split():
                                        tags_list.append('#{tag}'.format(
                                            tag=_type + re.sub(r"\W+", "_", tg_s) if _type else re.sub(r"\W+", "_",
                                                                                                       tg_s)))
                                else:
                                    tags_list.append('#{tag}'.format(
                                        tag=_type + re.sub(r"\W+", "_", tags) if _type else re.sub(r"\W+", "_",
                                                                                                   tags)))
                        else:
                            tags_list.append(config.get('znt.settings', 'body_messages_tags_no'))
                else:
                    tags_list.append(config.get('znt.settings', 'body_messages_tags_no'))
            else:
                return False

        except ValueError:
            tags_list.append(config.get('znt.settings', 'body_messages_tags_no'))
        else:
            return ' '.join(tags_list)

    def __create_settings_list(self):
        tags_list = []
        settings_list = []
        try:
            if self.options.zntsettingstag and self.macros.eventtags:
                for tags in self.macros.eventtags.split(', '):
                    if tags.find(':') != -1:
                        tag, value = re.split(r':+', tags, maxsplit=1)
                        if tag == config.get('znt.settings', 'trigger_settings_tag'):
                            tags_list.append('#{tag}_{value}'.format(
                                tag=config.get('znt.settings', 'trigger_settings_tag')
                                if config.get('znt.settings', 'trigger_settings_tag') else re.sub(r"\W+", "_", tag),
                                value=re.sub(r"\W+", "_", value)))
                            settings_list.append(value)
                        else:
                            continue
                    else:
                        continue
            else:
                self.zntsettings = False
        except Exception as err:
            self.logger.error("Exception occurred: {}".format(err), exc_info=config.get('logging', 'exc_info')), exit(1)
        else:
            self.zntsettings = {'tags': tags_list, config.get('znt.settings', 'trigger_settings_tag'): settings_list}
            self.logger.debug("Найдены тэги настроек: {}: {}".format(
                config.get('znt.settings', 'trigger_settings_tag'),
                ', '.join(self.zntsettings[config.get('znt.settings', 'trigger_settings_tag')])))

    def __create_mentions_list(self):
        try:
            if self.options.zntmentions and self.macros.eventtags:
                mentions_list = []
                for tags in self.macros.eventtags.split(', '):
                    if tags.find(':') != -1:
                        tag, value = re.split(r':+', tags, maxsplit=1)
                        if tag == config.get('znt.settings', 'trigger_info_mentions_tag'):
                            for username in value.split():
                                mentions_list.append(username)
                self.mentions = mentions_list
            else:
                return False
        except Exception as err:
            self.logger.error("Exception occurred: {}".format(err), exc_info=config.get('logging', 'exc_info')), exit(1)

    def __create_links_list(self, _bool=None, url=None, _type=None, url_list=None):
        try:
            if _bool:
                if url and (re.search(r'\w', url)):
                    return config.get('znt.settings', 'body_messages_url_template').format(url=url, icon=_type)
                else:
                    return config.get('znt.settings', 'body_messages_url_emoji_no_url')
            elif url_list:
                return url_list
            else:
                return False
        except ValueError:
            return config.get('znt.settings', 'body_messages_url_emoji_no_url')

    def __handling_settings(self):
        settings_send = next((x for x in self.zntsettings[config.get('znt.settings', 'trigger_settings_tag')]
                             if config.get('znt.settings', 'trigger_settings_tag_send') in x), None)
        settings_chart = next((x for x in self.zntsettings[config.get('znt.settings', 'trigger_settings_tag')]
                              if config.get('znt.settings', 'trigger_settings_tag_chart') in x), None)
        if settings_send:
            try:
                znts_send = str(settings_send.split('=')[1])
            except Exception as err:
                self.logger.error("Exception occurred: {}: {}".format(
                    config.get('znt.settings', 'trigger_settings_tag'), err),
                    exc_info=config.get('logging', 'exc_info')), exit(1)
            else:
                if znts_send == 'silent':
                    self.logger.warn("Отправка сообщения без оповещения: {}:'{}'".format(
                        config.get('znt.settings', 'trigger_settings_tag'), settings_send))
                    self.settings_not_notify = True
                elif znts_send == 'disable':
                    self.logger.warn("Отправка сообщения отменена: {}:'{}'".format(
                        config.get('znt.settings', 'trigger_settings_tag'), settings_send))
                    raise ZNTSettingTags(message="Отправка сообщения отменена", detail="Был найден тег {}:'{}'".format(
                        config.get('znt.settings', 'trigger_settings_tag'),
                        settings_send))
                else:
                    self.logger.warn("В тегэ {}:'{}' неизвестный параметр.".format(
                        config.get('znt.settings', 'trigger_settings_tag'), settings_send))

        if settings_chart:
            try:
                znts_chart = str(settings_chart.split('=')[1])
            except Exception as err:
                self.logger.error("Exception occurred: {}: {}".format(
                    config.get('znt.settings', 'trigger_settings_tag'), err),
                    exc_info=config.get('logging', 'exc_info')), exit(1)
            else:
                if znts_chart == 'disable':
                    self.logger.warn("Отправка сообщения без графиков: {}:'{}'.".format(
                        config.get('znt.settings', 'trigger_settings_tag'), settings_chart))
                    self.settings_chart_disable = True
                elif znts_chart == 'single':
                    self.logger.warn("Отправка сообщения c одним графиком: {}:'{}'.".format(
                        config.get('znt.settings', 'trigger_settings_tag'), settings_chart))
                    self.settings_chart_single = True
                elif znts_chart == 'group':
                    self.logger.warn("Отправка сообщения с группой графиков: {}:'{}'.".format(
                        config.get('znt.settings', 'trigger_settings_tag'), settings_chart))
                    self.settings_chart_group = True
                else:
                    self.logger.warn("В тегэ {}:'{}' неизвестный параметр.".format(
                        config.get('znt.settings', 'trigger_settings_tag'), settings_chart))

    def __settings_chart_period(self):
        if isinstance(self.zntsettings, dict) and not all(
                settings.find(config.get('znt.settings', 'trigger_settings_tag_graph_period')) and len(settings) > 0
                for settings in self.zntsettings[config.get('znt.settings', 'trigger_settings_tag')]):
            try:
                chart_period = next((x for x in self.zntsettings[config.get('znt.settings', 'trigger_settings_tag')] if config.get('znt.settings', 'trigger_settings_tag_graph_period') in x), None)
                znts_period = int(chart_period.split('=')[1])
            except Exception as err:
                self.logger.error("Exception occurred: {}: {}".format(
                    config.get('znt.settings', 'trigger_settings_tag'), err),
                    exc_info=config.get('logging', 'exc_info')), exit(1)
            else:
                self.logger.warn("Отправка сообщения с измененным периодом графиков: {}:'{}'.".format(
                    config.get('znt.settings', 'trigger_settings_tag'), chart_period))
                self.chart_period = znts_period
        elif self.options.graphs_period != 'default':
            self.chart_period = self.options.graphs_period
        else:
            self.chart_period = config.get('znt.settings', 'zabbix_graph_period_default')

    # def __settings_bot(self):
    #     if isinstance(self.zntsettings, dict) and not all(
    #             settings.find(config.get('znt.settings', 'trigger_settings_tag_graph_period')) and len(settings) > 0
    #             for settings in self.zntsettings[config.get('znt.settings', 'trigger_settings_tag')]):
    #         try:
    #             chart_period_raw = [i if i.find(config.get('znt.settings', 'trigger_settings_tag_graph_period')) == 0
    #                                 else False for i in self.zntsettings[config.get('znt.settings',
    #                                                                                 'trigger_settings_tag')]][0]
    #             chart_period = int(chart_period_raw.split('=')[1])
    #         except Exception as err:
    #             self.logger.error("Exception occurred: {}:{}, {}".format(
    #                 config.get('znt.settings', 'trigger_settings_tag'), chart_period_raw, err),
    #                 exc_info=config.get('logging', 'exc_info')), exit(1)
    #         else:
    #             self.chart_period = chart_period
    #     elif self.options.graphs_period != 'default':
    #         self.chart_period = self.options.graphs_period
    #     else:
    #         self.chart_period = config.get('znt.settings', 'zabbix_graph_period_default')

    def __init_bot(self):
        # _default = 'production'
        settings_raw = None
        settings_bot = next((x for x in self.zntsettings[config.get('znt.settings', 'trigger_settings_tag')]
                             if config.get('znt.settings', 'trigger_settings_tag_bot') in x), None)
        settings_bot_group = next((x for x in self.zntsettings[config.get('znt.settings', 'trigger_settings_tag')]
                                   if config.get('znt.settings', 'trigger_settings_tag_bot_group') in x), None)

        if settings_bot:  # Если указано имя бота в тэге znts:bot=@username
            try:
                znts_bot = str(settings_bot.split('=')[1])
            except Exception as err:
                self.logger.error("Exception occurred: {}:{}, {}".format(
                    config.get('znt.settings', 'trigger_settings_tag'), settings_raw, err),
                    exc_info=config.get('logging', 'exc_info')), exit(1)
            else:
                # Ищем имя бота отвечающего требованиям Telegram
                if re.search("^(?=.{5,35}$)@[a-zA-Z0-9_]+(?:bot|Bot)", znts_bot):
                    self.logger.debug("Поиск бота \"{}\"".format(znts_bot))
                    for bot in self.bot_list:
                        if bot['name'] == znts_bot:
                            self.bot_name = bot['name']
                            self.bot_token = bot['token']
                            self.bot_proxy_use = bot['proxy_use']
                            self.bot_proxy = bot['proxy']
                            self.logger.debug("Бот {} найден в БД.".format(self.bot_name))
                            return
                    self.logger.error("Отпрака сообщения на основании тега {}: {} отменена. "
                                      "Имя указанного бота \"{}\" не найдено в БД.".format(
                        config.get('znt.settings', 'trigger_settings_tag'), settings_bot, znts_bot))
                else:
                    self.logger.warn("Отпрака сообщения на основании тега {}: {} отменена. "
                                     "Имя указанного бота \"{}\" не отвечает требованиям Telegram.".format(
                        config.get('znt.settings', 'trigger_settings_tag'), settings_bot, znts_bot))

        elif settings_bot_group:  # Если указана группа в тэге znts:bot_group=dba
            try:
                znts_bot_group = str(settings_bot_group.split('=')[1])
            except Exception as err:
                self.logger.error("Exception occurred: {}:{}, {}".format(
                    config.get('znt.settings', 'trigger_settings_tag'), settings_raw, err),
                    exc_info=config.get('logging', 'exc_info')), exit(1)
            else:
                self.logger.debug("Поиск приоритетных ботов в группе \"{}\"".format(znts_bot_group))
                list_priority = []
                for znts_bot in self.bot_list:
                    if znts_bot['group'] == znts_bot_group:
                        list_priority.append(znts_bot['priority'])
                for znts_bot in self.bot_list:
                    if znts_bot['group'] == znts_bot_group and znts_bot['priority'] == min(list_priority):
                        self.bot_name = znts_bot['name']
                        self.bot_token = znts_bot['token']
                        self.bot_proxy_use = znts_bot['proxy_use']
                        self.bot_proxy = znts_bot['proxy']
                        self.logger.debug("Выбран бот {} с приоритетом {}.".format(self.bot_name, min(list_priority)))
                        return
                self.logger.error("Отпрака сообщения на основании тега {}: {} отменена. Ботов в группе {} не найдено. "
                                  "Добавьте бота в группу.".format(
                    config.get('znt.settings', 'trigger_settings_tag'), settings_bot_group, znts_bot_group))

        if len(self.send.bot) > 0 and len(self.send.bot_group) == 0:  # Указан только бот
            if re.search("^(?=.{5,35}$)@[a-zA-Z0-9_]+(?:bot|Bot)", self.send.bot):
                self.logger.debug("Поиск бота \"{}\" указаного в action.".format(self.send.bot))
                # self.logger.info("Отправка сообщения через бота из action: {}'".format(self.send.bot))
                for znts_bot in self.bot_list:
                    if znts_bot['name'] == self.send.bot:
                        self.bot_name = znts_bot['name']
                        self.bot_token = znts_bot['token']
                        self.bot_proxy_use = znts_bot['proxy_use']
                        self.bot_proxy = znts_bot['proxy']
                        self.logger.debug("Бот {} найден в БД.".format(self.send.bot))
                        return
                self.logger.error("Отпрака сообщения отменена. Бот {} не найден. Добавьте бота в БД.".format(
                    self.send.bot))
        elif len(self.send.bot) > 0 and len(self.send.bot_group) > 0:  # Указан бот и группа
            self.logger.debug("Поиск бота \"{}\" в группе \"{}\" указаного в action.".format(self.send.bot,
                                                                                             self.send.bot_group))
            for znts_bot in self.bot_list:
                if znts_bot['name'] == self.send.bot and znts_bot['group'] == self.send.bot_group:
                    self.bot_name = znts_bot['name']
                    self.bot_token = znts_bot['token']
                    self.bot_proxy_use = znts_bot['proxy_use']
                    self.bot_proxy = znts_bot['proxy']
                    self.logger.debug("Бот {} найден в БД.".format(self.send.bot))
                    return
                else:
                    self.bot_name = znts_bot['name']
                    self.bot_token = znts_bot['token']
                    self.bot_proxy_use = znts_bot['proxy_use']
                    self.bot_proxy = znts_bot['proxy']
                    self.logger.warn("Бот {0} найден в БД, но бот {0} в группу {1} не добавлен. "
                                     "Добавьте бота в группу или удалите группу их action.".format(self.send.bot,
                                                                                                   self.send.bot_group))
                    return
        elif len(self.send.bot) == 0 and len(self.send.bot_group) > 0:  # Указана только группа
            self.logger.debug("Поиск бота \"{}\" указаного в action.".format(self.send.bot))
            list_priority = []
            for znts_bot in self.bot_list:
                if znts_bot['group'] == self.send.bot_group:
                    list_priority.append(znts_bot['priority'])
            for znts_bot in self.bot_list:
                if znts_bot['group'] == self.send.bot_group and znts_bot['priority'] == min(list_priority):
                    self.bot_name = znts_bot['name']
                    self.bot_token = znts_bot['token']
                    self.bot_proxy_use = znts_bot['proxy_use']
                    self.bot_proxy = znts_bot['proxy']
                    self.logger.debug("Бот {} найден в БД.".format(self.send.bot))
                    return
            raise Exception("Отпрака сообщения отменена. Бот {} не найден. Добавьте бота в БД>.".format(self.send.bot))
        else:
            self.logger.debug("Поиск любого приоритетного бота в БД.")
            list_priority = []
            for znts_bot in self.bot_list:
                list_priority.append(znts_bot['priority'])

            for znts_bot in self.bot_list:
                if znts_bot['priority'] == min(list_priority):
                    self.bot_name = znts_bot['name']
                    self.bot_token = znts_bot['token']
                    self.bot_proxy_use = znts_bot['proxy_use']
                    self.bot_proxy = znts_bot['proxy']
                    self.logger.debug("Найден бот {} в БД.".format(znts_bot['name']))
                    break
