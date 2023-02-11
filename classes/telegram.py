# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
__author__ = "Sokolov Dmitry"
__maintainer__ = "Sokolov Dmitry"
__license__ = "MIT"
import re
import os
import json
import shutil
import time
from errno import ENOENT
from types import SimpleNamespace
from telebot import TeleBot
from telebot import apihelper
from config import *


class Telegram:


    def __init__(self, logger, send_to: str, send_from: str, chart_png, message: str, keyboard: bool,
                 token: str = None, proxy=False, disable_notification=False):
        self.logger = logger
        self.send_to = send_to
        self.chat_id = None
        self.chat_name = None
        self.chart_png = chart_png
        self.message = message
        self.disable_notification = disable_notification
        self.bot = TeleBot(token)
        if isinstance(proxy, dict):
            apihelper.proxy = json.loads(proxy)
        self.__send_messages()

    def get_cache(self, chat_name: str = None, chat_id: str = None):
        read_cache = None
        try:
            if not os.path.exists(config_cache_file):
                raise IOError(ENOENT, 'No such file or directory', config_cache_file)
        except Exception as err:
            self.logger.error("Exception occurred: {}".format(err), exc_info=config_exc_info)
            open(config_cache_file, 'a').close()
            self.logger.info("Cache file created in {}".format(config_cache_file))
        else:
            read_cache = open(config_cache_file, 'r').read()

        if read_cache:
            cache = json.loads(read_cache)

            if chat_name:
                for name, value in cache.items():
                    if chat_name == name:
                        return value['id']
                self.logger.warning('Имя чата "{chat_name}" не найдено в кеш-файле.'.format(chat_name=chat_name))
                return False
            elif chat_id:
                for name, value in cache.items():
                    if value['id'] == chat_id:
                        return dict(name=name, body=value)
                self.logger.info('Имя чата "{chat_id}" не соответствует имени в кеш-файле.'.format(
                    chat_id=self.chat_id,
                    cache_chat_id=name
                ))
                return False
            else:
                pass
        else:
            self.logger.warning("Чат '{chat_name}' не найден в кэш-файле.".format(chat_name=self.chat_name))
            return False

    def set_cache(self, chat_name: str, chat_id: str, chat_type: str, update: dict=None, cache=None):
        backup_file = config_cache_file_backup.format(date=time.strftime("%d%m%Y%H%M%S"))
        self.logger.info('Делаем бэкап кэш-файла: {} -> {}'.format(config_cache_file, backup_file))
        shutil.copyfile(src=config_cache_file, dst=backup_file)
        changed_chat_name = None
        f = open(config_cache_file, 'r+')
        r = f.read()
        if r:
            cache = json.loads(r)
        if not cache:
            cache = {chat_name: dict(type=str(chat_type), id=str(chat_id))}
        else:
            if not update:
                changed_chat_name = self.get_cache(chat_id=chat_id)
                if changed_chat_name and not chat_name == changed_chat_name['name']:
                    cache[chat_name] = cache.pop(changed_chat_name['name'])
                    update = dict(chat_name=changed_chat_name['name'], chat_id=changed_chat_name['body']['id'],
                                  update_type='chat_name', update_value=chat_name)
                elif changed_chat_name and chat_name == changed_chat_name['name']:
                    return True
                else:
                    cache[chat_name] = dict(type=str(chat_type), id=str(chat_id))
            else:
                cache[chat_name] = dict(type=str(chat_type), id=str(update['update_value']), old_id=str(chat_id))
        f.seek(0)
        f.write(json.dumps(cache, sort_keys=True, ensure_ascii=False, indent=4))
        f.truncate()
        f.close()
        if update or changed_chat_name:
            self.logger.info('Обновляем кэш-файл: "{chat_name}" ({chat_id}) -> {update_type}: {update_value}'.format(
                **update))
        else:
            self.logger.info('Добавляем в кэш-файл: "{chat_name}" ({chat_id})'.format(
                chat_id=chat_id, chat_name=chat_name))
        return True

    def get_send_id(self):
        try:
            chat = None
            if re.search('^[0-9]+$', self.send_to) or re.search('^-[0-9]+$', self.send_to):
                self.chat_id = self.send_to
            elif re.search('^@+[a-zA-Z0-9_]{5,}$', self.send_to):
                self.chat_id = self.send_to[1:]
            elif not self.send_to:
                raise ValueError('Username or groupname is not specified. You can use for username '
                                 '@[a-z,A-Z,0-9 and underscores] and for groupname any characters. ')
            else:
                self.chat_name = self.send_to

            cache_chat_id = self.get_cache(chat_name=self.chat_name, chat_id=self.chat_id)

            if cache_chat_id:
                self.chat_id = cache_chat_id
                return

            self.logger.info("Опрашиваем бота о чате (getUpdate)")
            get_updates_list = self.bot.get_updates(timeout=10)
            sum_del_update_id = 0
            while len([value.update_id for value in get_updates_list]) >= 100:
                sum_del_update_id += len([value.update_id for value in get_updates_list])
                get_updates_list = self.bot.get_updates(timeout=10,
                                                        offset=max([value.update_id for value in get_updates_list]))

            if sum_del_update_id > 0:
                self.logger.info("In getUpdate list was cleared {} messages. Submitted for processing {}.".format(
                    sum_del_update_id, len([value.update_id for value in get_updates_list])))

            for line in get_updates_list:
                if line.message:
                    chat = line.message.chat
                elif line.edited_message:
                    chat = line.edited_message.chat
                elif line.channel_post:
                    chat = line.channel_post.chat

                if chat.type in ["group", "supergroup"] and chat.title and chat.title == self.chat_name:
                    if not cache_chat_id:
                        self.set_cache(chat_name=str(chat.title), chat_id=str(chat.id), chat_type=str(chat.type),
                                       update=None)
                    self.bot.get_updates(timeout=10, offset=-1)
                    self.chat_id = chat.id
                    return

                if chat.type in ["channel"] and chat.title and chat.title == send_to:
                    if not send_id:
                        set_cache(send_to, chat.id, chat.type)
                    bot.get_updates(timeout=10, offset=-1)
                    return chat.id

                if chat.type in ["private"] and chat.username == send_to.replace("@", ""):
                    if not send_id:
                        set_cache(send_to, chat.id, chat.type)
                    bot.get_updates(timeout=10, offset=-1)
                    return chat.id

            raise ValueError(
                'Имя чата не найдено в кеш-файле. Не получен доступ или бот не добавлен в чат "{sendto}" '
                '(Добавьте бота в чат и/или отправьте сообщение @{bot})'.format(
                    bot=self.bot.get_me().username,
                    sendto=self.chat_id))
        except Exception as err:
            self.logger.error("Exception occurred: {}".format(err), exc_info=config_exc_info), exit(1)


    def gen_markup(self, eventid):
        markup = InlineKeyboardMarkup()
        markup.row_width = zabbix_keyboard_row_width
        markup.add(
            InlineKeyboardButton(zabbix_keyboard_button_message,
                                 callback_data='{}'.format(json.dumps(dict(action="messages", eventid=eventid)))),
            InlineKeyboardButton(zabbix_keyboard_button_acknowledge,
                                 callback_data='{}'.format(json.dumps(dict(action="acknowledge", eventid=eventid)))),
            InlineKeyboardButton(zabbix_keyboard_button_history,
                                 callback_data='{}'.format(json.dumps(dict(action="history", eventid=eventid)))),
            InlineKeyboardButton(zabbix_keyboard_button_history,
                                 callback_data='{}'.format(json.dumps(dict(action="last value", eventid=eventid)))),
            InlineKeyboardButton(zabbix_keyboard_button_history,
                                 callback_data='{}'.format(json.dumps(dict(action="graphs", eventid=eventid)))))
        return markup

    def __send_messages(self):
        try:
            self.get_send_id()
            if self.message and self.chat_id:
                if self.chart_png and isinstance(self.chart_png, list):
                    try:
                        graphs_png[0].caption = message
                        graphs_png[0].parse_mode = "HTML"
                        bot.send_media_group(chat_id=sent_id, media=graphs_png, disable_notification=disable_notification)
                    except apihelper.ApiException as err:
                        if 'migrate_to_chat_id' in err.result.text:
                            migrate_group_id(sent_to, sent_id, err)
                            send_messages(sent_to, message, graphs_png, settings_keyboard)
                        else:
                            self.logger.error("Exception occurred in Api Telegram: {}".format(err), exc_info=config_exc_info),
                            exit(1)
                    except Exception as err:
                        self.logger.error("Exception occurred: {}".format(err), exc_info=config_exc_info),exit(1)
                    else:
                        self.logger.info('Bot @{busername}({bid}) send media group to "{sent_to}" ({sent_id}).'.format(
                            sent_to=sent_to, sent_id=sent_id, busername=bot.get_me().username, bid=bot.get_me().id))
                        exit(0)
                elif self.chart_png and self.chart_png.get('img'):
                    try:
                        response_tg = self.bot.send_photo(
                            chat_id=self.chat_id, photo=self.chart_png.get('img'), caption=self.message,
                            parse_mode="HTML", reply_markup=gen_markup(eventid) if zabbix_keyboard and settings_keyboard else None,
                            disable_notification=self.disable_notification)
                    except apihelper.ApiException as err:
                        self.logger.error(err)
                        if 'migrate_to_chat_id' in err.result_json['parameters']:
                            self.logger.warning('Миграция группы "{chat_name}" ({chat_id}) -> ({new_chat_id})'.format(
                                chat_name=self.chat_name,
                                chat_id=self.chat_id,
                                new_chat_id=err.result_json['parameters']['migrate_to_chat_id'])
                            )

                            self.set_cache(chat_name=self.chat_name, chat_id=self.chat_id, chat_type='supergroup',
                                           update=dict(chat_name=self.chat_name, chat_id=self.chat_id,
                                                       update_type='chat_id',
                                                       update_value=err.result_json['parameters']['migrate_to_chat_id']))
                            self.__send_messages()
                        else:
                            self.logger.crirical("Exception occurred in Api Telegram: {}".format(err),
                                                 exc_info=config_exc_info)
                            raise SystemExit(1)
                    except Exception as err:
                        self.logger.critical("Exception occurred: {}".format(err), exc_info=config_exc_info)
                        raise SystemExit(1)
                    else:
                        if not response_tg.chat.title == self.chat_name:
                            self.logger.warning(
                                'Вы отправляете сообщение в чат "{chat_name}", но оно имя было изменено на '
                                '"{new_chat_name}". Измените получателя "Send to" в User -> media'.format(
                                    chat_name=self.chat_name, new_chat_name=response_tg.chat.title))
                        self.logger.info('Bot @{bot_name}({bot_id}) send photo to "{chat_name}" ({chat_id}).'.format(
                            chat_name=self.chat_name, chat_id=self.chat_id, bot_name=self.bot.get_me().username,
                            bot_id=self.bot.get_me().id))
                else:
                    try:
                        response_tg = self.bot.send_message(
                            chat_id=self.chat_id, text=self.message, parse_mode="HTML", disable_web_page_preview=True,
                            reply_markup=gen_markup(eventid) if zabbix_keyboard and settings_keyboard else None,
                            disable_notification=self.disable_notification)
                    except apihelper.ApiException as err:
                        self.logger.error(err)
                        if 'migrate_to_chat_id' in err.result_json['parameters']:
                            self.logger.warning('Миграция группы "{chat_name}" ({chat_id}) -> ({new_chat_id})'.format(
                                chat_name=self.chat_name,
                                chat_id=self.chat_id,
                                new_chat_id=err.result_json['parameters']['migrate_to_chat_id'])
                            )

                            self.set_cache(chat_name=self.chat_name,
                                           chat_id=self.chat_id,
                                           chat_type='supergroup',
                                           update=dict(chat_name=self.chat_name, chat_id=self.chat_id,
                                                       update_type='chat_id',
                                                       update_value=err.result_json['parameters']['migrate_to_chat_id']))
                            self.__send_messages()
                        else:
                            self.logger.crirical("Exception occurred in Api Telegram: {}".format(err),
                                                 exc_info=config_exc_info)
                            raise SystemExit(1)
                    except Exception as err:
                        self.logger.error("Exception occurred: {}".format(err), exc_info=config_exc_info), exit(1)
                    else:
                        if not response_tg.chat.title == self.chat_name:
                            self.logger.warning('Вы отправляете сообщение в чат "{chat_name}", но оно было изменено на '
                                                '"{new_chat_name}". Измените получателя "Send to" в '
                                                'User -> media'.format(chat_name=self.chat_name,
                                                                       new_chat_name=response_tg.chat.title))
                        self.logger.info('Bot @{bot_name}({bot_id}) send message to "{chat_name}" ({chat_id}).'.format(
                            chat_name=self.chat_name, chat_id=self.chat_id, bot_name=self.bot.get_me().username,
                            bot_id=self.bot.get_me().id))
                        exit(0)
        except Exception as err:
            self.logger.crirical("Exception occurred: {}".format(err), exc_info=config_exc_info)
            raise SystemExit(1)

