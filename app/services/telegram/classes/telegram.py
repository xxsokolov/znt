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
import json

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telebot import apihelper

from app.databases.database import SessionLocal
from app.services.telegram.config import *
from app.api import models


class Telegram:

    def __init__(self, logger, send_to: str, chart_png, message: str, keyboard: bool,
                 token: str = None, proxy_use=False, proxy=None, disable_notification=False):
        self.logger = logger
        self.send_to = send_to
        self.chat_id = None
        self.chat_name = None
        self.chart_png = chart_png
        self.message = message
        self.disable_notification = disable_notification
        self.bot = TeleBot(token)
        # apihelper.API_URL = "http://localhost:8081/bot{0}/{1}"
        if proxy_use:
            apihelper.proxy = {proxy.proto: proxy.url}
        self.response_tg = None
        self.response_tg_json = None

        self.db = SessionLocal()
        self.__send_messages()

    def get_chat_db(self, chat_name: str = None, chat_id: str = None):
        try:
            chat_list_db = [{column.name: getattr(chat, column.name) for column in chat.__table__.columns} for chat in self.db.query(
                models.chat.Chat).all()]
        except Exception as err:
            raise err
        finally:
            self.db.close()

        if len(chat_list_db) > 0:
            if chat_name:
                for chat_db in chat_list_db:
                    if chat_name == chat_db.get("name"):
                        return chat_db["chat_id"]
                self.logger.warning('Имя чата "{chat_name}" не найдено в кеш-файле.'.format(chat_name=chat_name))
                return False
            elif chat_id:
                for chat_db in chat_list_db:
                    if chat_id == chat_db.get("chat_id"):
                        return chat_db
                self.logger.info('Имя чата "{chat_id}" не соответствует имени в кеш-файле.'.format(
                    chat_id=chat_id
                ))
                return False
            else:
                pass
        else:
            self.logger.warning("Чат '{chat_name}' не найден в кэш-файле.".format(chat_name=chat_name))
            return False

    def set_chat_db(self, chat_name: str, chat_id: str, chat_type: str, update: dict, cache=None):
        changed_chat_name = None

        try:
            if not update:
                chat_data = dict(name=chat_name, chat_id=chat_id, chat_id_prev=None, type=chat_type)
                db_chat = app.api.models.chat.Chat(**chat_data)
                self.db.add(db_chat)
                self.db.commit()
                self.db.refresh(db_chat)
            else:
                chat_data = dict(name=chat_name, chat_id=chat_id, chat_id_prev=None, type=chat_type)
                # db_chat = models.chat.Chat(**chat_data)
                update_chat = self.db.query(app.api.models.chat.Chat)\
                    .filter(app.api.models.chat.Chat.name == chat_name and app.api.models.chat.Chat.chat_id == chat_id)\
                    .update(dict(chat_id=update['update_value'], type=chat_type, chat_id_prev=chat_id))
                self.db.commit()
                # self.db.refresh(db_chat)
        except Exception as err:
            raise err
        finally:
            self.db.close()

        # if not cache:
        #     cache = {chat_name: dict(type=str(chat_type), id=str(chat_id))}
        # else:
        #     if not update:
        #         changed_chat_name = self.get_cache(chat_id=chat_id)
        #         if changed_chat_name and not chat_name == changed_chat_name['name']:
        #             cache[chat_name] = cache.pop(changed_chat_name['name'])
        #             update = dict(chat_name=changed_chat_name['name'], chat_id=changed_chat_name['body']['id'],
        #                           update_type='chat_name', update_value=chat_name)
        #         elif changed_chat_name and chat_name == changed_chat_name['name']:
        #             return True
        #         else:
        #             cache[chat_name] = dict(type=str(chat_type), id=str(chat_id))
        #     else:
        #         cache[chat_name] = dict(type=str(chat_type), id=str(update['update_value']), old_id=str(chat_id))
        #
        if update or changed_chat_name:
            self.logger.info('Обновляем кэш-файл: "{chat_name}" ({chat_id}) -> {update_type}: {update_value}'.format(
                **update))
        else:
            self.logger.info('Добавляем в кэш-файл: "{chat_name}" ({chat_id})'.format(
                chat_id=chat_id, chat_name=chat_name))
        return True

    def get_send_id(self):
        try:
            # raise Exception('test err')
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

            cache_chat_id = self.get_chat_db(chat_name=self.chat_name, chat_id=self.chat_id)

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
                    self.set_chat_db(chat_name=str(chat.title), chat_id=str(chat.id), chat_type=str(chat.type), update=None)
                self.bot.get_updates(timeout=10, offset=-1)
                self.chat_id = chat.id
                return

            if chat.type in ["channel"] and chat.title and chat.title == send_to:
                if not send_id:
                    set_cache(send_to, chat.id, chat.type)
                bot.get_updates(timeout=10, offset=-1)
                return chat.id

            if chat.type in ["private"] and chat.username == self.chat_name.replace("@", ""):
                self.bot.get_updates(timeout=10, offset=-1)
                self.chat_id = chat.id
                return chat.id

            raise ValueError(
                "Имя чата не найдено в таблице chat. Бот не имеет доступа к чтению сообщений в чате или он не добавлен в чат '{sendto}' "
                "(Добавьте бота @{bot} в чат, дайте права на чтение сообщений и отправьте сообщение в чат.)".format(
                    bot=self.bot.get_me().username,
                    sendto=self.send_to))
        except Exception as err:
            self.logger.exception("Ошибка: {}".format(err), exc_info=config_exc_info)
            raise err


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
        self.get_send_id()
        if self.message and self.chat_id:
            if isinstance(self.chart_png, list) and self.chart_png[0]:
                try:
                    chart_png = [InputMediaPhoto(x) for x in self.chart_png]
                    chart_png[0].caption = self.message
                    chart_png[0].parse_mode = "HTML"
                    self.response_tg = self.bot.send_media_group(chat_id=self.chat_id, media=chart_png, disable_notification=self.disable_notification)
                except apihelper.ApiException as err:
                    # Проверяем на миграцию chat_id
                    if 'migrate_to_chat_id' in err.result_json['parameters']:
                        self.logger.warning('Миграция группы "{chat_name}" ({chat_id}) -> ({new_chat_id})'.format(
                            chat_name=self.chat_name,
                            chat_id=self.chat_id,
                            new_chat_id=err.result_json['parameters']['migrate_to_chat_id'])
                        )
                        # Записываем в бд новый chat_id после миграции группы
                        self.set_chat_db(chat_name=self.chat_name, chat_id=self.chat_id, chat_type='supergroup',
                                         update=dict(chat_name=self.chat_name, chat_id=int(self.chat_id),
                                                   update_type='chat_id',
                                                   update_value=int(err.result_json['parameters']['migrate_to_chat_id'])))
                        # Повторно запускаем отправку сообщения
                        self.__send_messages()
                    else:
                        self.logger.critical("Ошибка в Api Telegram: {}".format(err),
                                             exc_info=config_exc_info)
                        raise err
                except Exception as err:
                    self.logger.critical("Ошибка: {}".format(err), exc_info=config_exc_info)
                    raise SystemExit(1)
                else:
                    if not self.response_tg[0].chat.title == self.chat_name:
                        self.logger.warning(
                            'Вы отправляете сообщение в чат "{chat_name}", но имя было изменено на '
                            '"{new_chat_name}". Измените получателя "Send to" в Zabbix: User -> media'.format(
                                chat_name=self.chat_name, new_chat_name=self.response_tg[0].chat.title))
                    self.logger.info('Бот @{bot_name}({bot_id}) отправил фото графиков в "{chat_name}" ({chat_id}).'.format(
                        chat_name=self.chat_name, chat_id=self.chat_id, bot_name=self.bot.get_me().username,
                        bot_id=self.bot.get_me().id))
                    self.response_tg_json = [x.json for x in self.response_tg]
            else:
                try:
                    self.response_tg = self.bot.send_message(
                        chat_id=self.chat_id, text=self.message, parse_mode="HTML", disable_web_page_preview=True,
                        disable_notification=self.disable_notification)
                except apihelper.ApiException as err:
                    # Проверяем на миграцию chat_id
                    if 'migrate_to_chat_id' in err.result_json['parameters']:
                        self.logger.warning('Миграция группы "{chat_name}" ({chat_id}) -> ({new_chat_id})'.format(
                            chat_name=self.chat_name,
                            chat_id=self.chat_id,
                            new_chat_id=err.result_json['parameters']['migrate_to_chat_id'])
                        )
                        # Записываем в бд новый chat_id после миграции группы
                        self.set_chat_db(chat_name=self.chat_name, chat_id=self.chat_id, chat_type='supergroup',
                                         update=dict(chat_name=self.chat_name, chat_id=int(self.chat_id),
                                                   update_type='chat_id',
                                                   update_value=int(
                                                       err.result_json['parameters']['migrate_to_chat_id'])))
                        # Повторно запускаем отправку сообщения
                        self.__send_messages()
                    else:
                        self.logger.critical("Ошибка в Api Telegram: {}".format(err),
                                             exc_info=config_exc_info)
                        raise err
                except Exception as err:
                    self.logger.critical("Ошибка: {}".format(err), exc_info=config_exc_info)
                    raise SystemExit(1)
                else:
                    if not self.response_tg[0].chat.title == self.chat_name:
                        self.logger.warning(
                            'Вы отправляете сообщение в чат "{chat_name}", но имя было изменено на '
                            '"{new_chat_name}". Измените получателя "Send to" в Zabbix: User -> media'.format(
                                chat_name=self.chat_name, new_chat_name=self.response_tg[0].chat.title))
                    self.logger.info('Бот @{bot_name}({bot_id}) отправил сообщение в "{chat_name}" ({chat_id}).'.format(
                        chat_name=self.chat_name, chat_id=self.chat_id, bot_name=self.bot.get_me().username,
                        bot_id=self.bot.get_me().id))
                    self.response_tg_json = [x.json for x in self.response_tg]
