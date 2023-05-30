# -*- coding: utf-8 -*-
####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################
import re
import json

# from sqlalchemy.orm import joinedload
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telebot import apihelper

from app.databases.database import SessionLocal
from app import config, logger
from app.api import models


class Telegram:

    def __init__(self, send_to: str, chart_png, message: str, keyboard: bool,
                 token: str = None, proxy_use=False, proxy=None, disable_notification=False):
        self.logger = logger.log
        self.send_to = send_to
        self.chat_id = None
        self.chat_name = None
        self.topic_name = None
        self.topic_id = None
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
            chat_list_db = [{column.name: getattr(chat, column.name) for column in chat.__table__.columns} for chat in self.db.query(models.chat.Chat).all()]
        except Exception as err:
            raise err
        finally:
            self.db.close()

        if len(chat_list_db) > 0:
            if chat_name:
                for chat_db in chat_list_db:
                    if chat_name == chat_db["name"]:
                        return chat_db
                self.logger.warning('Имя чата "{chat_name}" не найдено в таблице chat.'.format(chat_name=chat_name))
                return False
            elif chat_id:
                for chat_db in chat_list_db:
                    if chat_id == str(chat_db['chat_id']):
                        return chat_db
                self.logger.info('Чат "{chat_id}" не найден в таблице chat.'.format(
                    chat_id=chat_id
                ))
                return False
            else:
                pass
        else:
            self.logger.warning("Чат '{chat_name}' не найден в таблице chat.".format(chat_name=chat_name))
            return False

    def get_topic_db(self, chat_id: str = None, topic_id: str = None, topic_name: str = None):
        try:
            join_chat_topic = []
            for chat in self.db.query(models.chat.Chat).join(models.topic.Topic).filter(models.chat.Chat.chat_id == chat_id).all():
                result_dict = {column.name: getattr(chat, column.name) for column in chat.__table__.columns}
                topic_list = []
                for topic in chat.topic:
                    topic = {column.name: getattr(topic, column.name) for column in topic.__table__.columns}
                    topic_list.append(topic)
                result_dict["topic"] = topic_list
                join_chat_topic.append(result_dict)


            #
            # from pydantic import parse_obj_as
            # from typing import List
            #
            # yyyy = parse_obj_as(models.chat.Chat, xxx.all())
            #
            # topic_list_db = [{column.name: getattr(chat, column.name) for column in chat.__table__.columns} for chat in self.db.query(models.chat.Chat).join(models.topic.Topic).all()]

        except Exception as err:
            raise err
        finally:
            self.db.close()

        if len(join_chat_topic) > 0:
            if topic_name:
                for chat in join_chat_topic:
                    for topic in chat['topic']:
                        if topic_name == topic["name"]:
                            return topic
                self.logger.warning('Имя топика "{topic_name}" не найдено в таблице topic.'.format(topic_name=topic_name))
                return False
            elif topic_id:
                for chat in join_chat_topic:
                    for topic in chat['topic']:
                        if topic_id == str(topic['topic_id']):
                            return topic
                self.logger.info('Ид топика "{topic_id}" не найдено в таблице topic.'.format(topic_id=topic_id))
                return False
            else:
                pass
        else:
            self.logger.warning("Топик '{topic_name}' не найден в таблице topic.".format(topic_name=topic_name))
            return False

    def set_chat_db(self, chat_name: str, chat_id: str, chat_type: str, update: dict=None, cache=None):
        changed_chat_name = None

        try:
            if not update:
                chat_data = dict(name=chat_name, chat_id=chat_id, chat_id_prev=None, type=chat_type)
                db_chat = models.chat.Chat(**chat_data)
                self.db.add(db_chat)
                self.db.commit()
                self.db.refresh(db_chat)
            else:
                chat_data = dict(name=chat_name, chat_id=chat_id, chat_id_prev=None, type=chat_type)
                # db_chat = models.chat.Chat(**chat_data)
                update_chat = self.db.query(models.chat.Chat)\
                    .filter(models.chat.Chat.name == chat_name and models.chat.Chat.chat_id == chat_id)\
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
            self.logger.info('Обновляем в таблице chat: "{chat_name}" ({chat_id}) -> {update_type}: {update_value}'.format(
                **update))
        else:
            self.logger.info('Добавляем в таблицу chat: "{chat_name}" ({chat_id})'.format(
                chat_id=chat_id, chat_name=chat_name))
        return True

    def set_topic_db(self, chat_id: str, topic_id: str, topic_name: str, update: dict=None, cache=None):
        changed_chat_name = None

        try:
            if not update:
                id_chat_table = self.db.query(models.chat.Chat).filter(models.chat.Chat.chat_id == chat_id).first()
                topic_data = dict(name=topic_name, topic_id=topic_id, chat_id=id_chat_table.id)
                db_topic = models.topic.Topic(**topic_data)
                self.db.add(db_topic)
                self.db.commit()
                self.db.refresh(db_topic)
            else:
                chat_data = dict(name=chat_name, chat_id=chat_id, chat_id_prev=None, type=chat_type)
                # db_chat = models.chat.Chat(**chat_data)
                update_chat = self.db.query(models.chat.Chat)\
                    .filter(models.chat.Chat.name == chat_name and models.chat.Chat.chat_id == chat_id)\
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
            self.logger.info('Добавляем в таблицу topic: {topic_name}'.format(topic_name=topic_name))
        return True

    def get_send_id(self):
        try:
            cache_topic_id = None
            cache_chat_id = None
            chat = None
            # Указан ид или ид с топиком
            if re.search(r"^[0-9]+$|^-[0-9]+$", self.send_to):
                self.chat_id = self.send_to
            elif re.search(r"^([0-9]+|-[0-9]+):([0-9]+)$", self.send_to):
                self.chat_id, self.topic_id = self.send_to.split(sep=':')
            elif re.search(r"^([0-9]+|-[0-9]+):([\S]+)$", self.send_to):
                self.chat_id, self.topic_name = self.send_to.split(sep=':')
            # Указан юзернайм
            elif re.search(r"^@+[a-zA-Z0-9_]{5,}$", self.send_to):
                self.chat_name = self.send_to[1:]

            # Указан имя группы и топик
            elif re.search(r"^(.*):(.*)$", self.send_to):
                self.chat_name, self.topic_name = self.send_to.split(sep=':')


            elif not self.send_to:
                raise ValueError('Username or groupname is not specified. You can use for username '
                                 '@[a-z,A-Z,0-9 and underscores] and for groupname any characters. ')
            else:
                self.chat_name = self.send_to
            # Опрашиваем таблицу chat
            cache_chat_id = self.get_chat_db(chat_name=self.chat_name, chat_id=self.chat_id)

            # Опрашиваем таблицу topic
            if (self.topic_id or self.topic_name) and cache_chat_id and cache_chat_id['type'] == 'supergroup':
                cache_topic_id = self.get_topic_db(chat_id=cache_chat_id['chat_id'], topic_id=self.topic_id,
                                                   topic_name=self.topic_name)

            if not cache_chat_id:
                self.get_update(type='chat')
            else:
                # супергруппа + найден топик в бд
                if cache_chat_id['type'] == 'supergroup' and cache_topic_id:
                    self.chat_id = cache_chat_id['chat_id']
                    self.chat_name = cache_chat_id['name']
                    self.topic_id = cache_topic_id["topic_id"]
                    self.topic_name = cache_topic_id['name']
                    return
                # не супергруппа + найден топик в бд
                elif not cache_chat_id['type'] == 'supergroup' and cache_topic_id:
                    self.chat_id = cache_chat_id['chat_id']
                    self.chat_name = cache_chat_id['name']
                    self.logger.info('Данная группа не содержит топиков.'.format())
                    return
                # ид или имя топика + супергруппа + не найден топик в бд
                elif (self.topic_id or self.topic_name) and cache_chat_id['type'] == 'supergroup' and not cache_topic_id:
                    self.chat_id = cache_chat_id['chat_id']
                    self.chat_name = cache_chat_id['name']
                    self.get_update(type='topic')
                else:
                    self.chat_id = cache_chat_id['chat_id']
                    self.chat_name = cache_chat_id['name']
                    return
        except Exception as err:
            self.logger.exception("Ошибка: {}".format(err), exc_info=config.get('core', 'exc_info'))
            raise err

    def get_update(self, type: str='chat'):
        try:
            self.logger.info("Отправляем запрос в Telegram API (getUpdate)")
            get_updates_list = self.bot.get_updates(timeout=10)
            # if
            sum_del_update_id = 0
            while len([value.update_id for value in get_updates_list]) >= 100:
                sum_del_update_id += len([value.update_id for value in get_updates_list])
                get_updates_list = self.bot.get_updates(timeout=10,
                                                        offset=max([value.update_id for value in get_updates_list]))

            if sum_del_update_id > 0:
                self.logger.info("In getUpdate list was cleared {} messages. Submitted for processing {}.".format(
                    sum_del_update_id, len([value.update_id for value in get_updates_list])))

            for line in get_updates_list:
                # Поиск добавления в группы, каналы
                if line.my_chat_member:
                    chat = line.my_chat_member.chat
                    if type == 'chat' and chat.title and self.chat_name and chat.title == self.chat_name:
                        self.chat_id = chat.id
                        self.set_chat_db(chat_name=str(chat.title), chat_id=str(chat.id), chat_type=str(chat.type))
                        self.bot.get_updates(timeout=10, offset=-1)
                        return
                # Поиск в сообщениях группы
                elif line.message:
                    chat = line.message.chat
                    if type == 'chat' and chat.type in ["group", "supergroup"] and chat.title:
                        if self.chat_id and str(chat.id) == self.chat_id:
                            self.chat_id = str(chat.id)
                            self.chat_name = chat.title
                            self.set_chat_db(chat_name=str(chat.title), chat_id=str(chat.id), chat_type=str(chat.type))
                            self.bot.get_updates(timeout=10, offset=-1)
                            return
                        elif self.chat_name and chat.title == self.chat_name:
                            self.chat_id = str(chat.id)
                            self.chat_name = chat.title
                            self.set_chat_db(chat_name=str(chat.title), chat_id=str(chat.id), chat_type=str(chat.type))
                            self.bot.get_updates(timeout=10, offset=-1)
                            return

                    # if not cache_topic_id and self.topic_name and self.topic_id:
                    #     self.set_topic_db(chat_id=str(chat.id), topic_name=str(self.topic_name),
                    #                       topic_id=str(self.topic_id), update=None)
                    # else:
                    #     self.logger.warning(
                    #         'Топик {topic} не найден в чате: "{chat_name}" ({chat_id})'.format(
                    #             topic=self.topic, chat_name=self.chat_name, chat_id=self.chat_id))

                    if type == 'topic' and line.message.forum_topic_created:
                        if self.chat_id and str(chat.id) == str(self.chat_id):
                            if self.topic_id and str(line.message.id) == self.topic_id:
                                self.topic_id = str(line.message.id)
                                self.topic_name = line.message.forum_topic_created.name
                                self.set_topic_db(chat_id=str(chat.id), topic_name=str(self.topic_name),
                                                  topic_id=str(self.topic_id), update=None)
                                self.bot.get_updates(timeout=10, offset=-1)
                                return
                            if self.topic_name and str(line.message.forum_topic_created.name) == self.topic_name:
                                self.topic_id = str(line.message.id)
                                self.topic_name = line.message.forum_topic_created.name
                                self.set_topic_db(chat_id=str(chat.id), topic_name=str(self.topic_name),
                                                  topic_id=str(self.topic_id), update=None)
                                self.bot.get_updates(timeout=10, offset=-1)
                                return
                            # self.logger.warning('Топик {topic} не найден в чате: "{chat_name}" ({chat_id})'.format(
                            #     topic=self.topic_id, chat_name=self.chat_name, chat_id=self.chat_id))

                    if type == 'topic' and line.message.is_topic_message:
                        if self.chat_id and str(chat.id) == str(self.chat_id):
                            if self.topic_id and str(line.message.message_thread_id) == self.topic_id:
                                self.topic_id = str(line.message.message_thread_id)
                                self.topic_name = line.message.reply_to_message.forum_topic_created.name
                                self.set_topic_db(chat_id=str(chat.id), topic_name=str(self.topic_name),
                                                  topic_id=str(self.topic_id), update=None)
                                self.bot.get_updates(timeout=10, offset=-1)
                                return
                            if self.topic_name and line.message.reply_to_message.forum_topic_created.name == self.topic_name:
                                self.topic_id = str(line.message.message_thread_id)
                                self.topic_name = line.message.reply_to_message.forum_topic_created.name
                                self.set_topic_db(chat_id=str(chat.id), topic_name=str(self.topic_name),
                                                  topic_id=str(self.topic_id), update=None)
                                self.bot.get_updates(timeout=10, offset=-1)
                                return

                    # if chat.is_forum and self.topic_name and not self.topic_id and line.message.forum_topic_created:
                    #     if line.message.forum_topic_created.name == self.topic_name:
                    #         self.topic_id = line.message.message_thread_id
                    #         self.topic_name = line.message.forum_topic_created.name
                    if type == 'chat' and chat.type in ["private"] and chat.username and self.chat_name and chat.username == self.chat_name.replace("@", ""):
                        self.chat_id = line.message.chat.id
                        self.set_chat_db(chat_name=str(chat.username), chat_id=str(chat.id), chat_type=str(chat.type))
                        self.bot.get_updates(timeout=10, offset=-1)
                        return
                # elif line.edited_message:
                #     chat = line.edited_message.chat
                # Поиск в постах канала
                elif line.channel_post:
                    chat = line.channel_post.chat
                    if type == 'chat' and chat.title and self.chat_name and chat.title == self.chat_name:
                        self.chat_id = chat.id
                        self.set_chat_db(chat_name=str(chat.title), chat_id=str(chat.id), chat_type=str(chat.type),
                                         update=None)
                        self.bot.get_updates(timeout=10, offset=-1)
                        return
            if type == 'chat':
                raise ValueError(
                    'Упоминание чата "{sendto}" в истории не найдено. Возможно, бот не имеет доступа к чтению сообщений в чате/группе/канале или он не добавлен в "{sendto}"'
                    '(Добавьте бота @{bot} в чат/группу/канал, выдайте права на чтение сообщений и отправьте любое сообщение в чат.)'.format(
                    bot=self.bot.get_me().username,
                    sendto=self.send_to))
            elif type == 'topic':
                raise ValueError(
                    'Упоминание топика в истории группы "{sendto}" не найдено. Возможно, топик не существует в группе или был переименован. Попробуйте отправить сообщение в топик'.format(
                        bot=self.bot.get_me().username,
                        sendto=self.send_to))
        except Exception as err:
            self.logger.exception("Ошибка: {}".format(err), exc_info=config.get('core', 'exc_info'))
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
            if isinstance(self.chart_png, list) and any(True if x else False for x in self.chart_png):
                try:
                    chart_png = [InputMediaPhoto(x) for x in self.chart_png]
                    chart_png[0].caption = self.message
                    chart_png[0].parse_mode = "HTML"
                    self.response_tg = self.bot.send_media_group(
                        chat_id=self.chat_id,
                        media=chart_png,
                        reply_to_message_id=self.topic_id if self.topic_id else 0,
                        disable_notification=self.disable_notification
                    )
                except apihelper.ApiException as err:
                    # Проверяем на миграцию chat_id
                    if 'parameters' in err.result_json and 'migrate_to_chat_id' in err.result_json['parameters']:
                        self.logger.warning('Зафиксирована миграция группы "{chat_name}" ({chat_id}) -> ({new_chat_id})'.format(
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
                                             exc_info=config.get('core', 'exc_info'))
                        raise err
                except Exception as err:
                    self.logger.critical("Ошибка: {}".format(err), exc_info=config.get('core', 'exc_info'))
                    raise SystemExit(1)
                else:
                    if not self.response_tg[0].chat.title == self.chat_name:
                        self.logger.warning(
                            'Вы отправляете сообщение в чат "{chat_name}", но имя было изменено на '
                            '"{new_chat_name}". Измените получателя "Send to" в Zabbix: User -> media'.format(
                                chat_name=self.chat_name, new_chat_name=self.response_tg[0].chat.title))
                    if self.topic_id:
                        self.logger.info(
                            'Бот @{bot_name} ({bot_id}) отправил фото графиков в "{chat_name}" ({chat_id}), топик "{topic_name}" ({topix_id})'.format(
                                chat_name=self.chat_name, chat_id=self.chat_id, bot_name=self.bot.get_me().username,
                                topic_name=self.topic_name, topix_id=self.topic_id, bot_id=self.bot.get_me().id))
                    else:
                        self.logger.info('Бот @{bot_name} ({bot_id}) отправил фото графиков в чат "{chat_name}" ({chat_id}).'.format(
                            chat_name=self.chat_name, chat_id=self.chat_id, bot_name=self.bot.get_me().username,
                            bot_id=self.bot.get_me().id))
                    self.response_tg_json = [x.json for x in self.response_tg]
            else:
                try:
                    self.response_tg = self.bot.send_message(
                        chat_id=self.chat_id,
                        text=self.message,
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                        reply_to_message_id=self.topic_id if self.topic_id else 0,
                        disable_notification=self.disable_notification
                    )
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
                                             exc_info=config.get('core', 'exc_info'))
                        raise err
                except Exception as err:
                    self.logger.critical("Ошибка: {}".format(err), exc_info=config.get('core', 'exc_info'))
                    raise SystemExit(1)
                else:
                    if not self.response_tg.chat.title == self.chat_name:
                        self.logger.warning(
                            'Вы отправляете сообщение в чат "{chat_name}", но имя было изменено на '
                            '"{new_chat_name}". Измените получателя "Send to" в Zabbix: User -> media'.format(
                                chat_name=self.chat_name, new_chat_name=self.response_tg.chat.title))
                    self.logger.info('Бот @{bot_name}({bot_id}) отправил сообщение в "{chat_name}" ({chat_id}).'.format(
                        chat_name=self.chat_name, chat_id=self.chat_id, bot_name=self.bot.get_me().username,
                        bot_id=self.bot.get_me().id))
                    self.response_tg_json = self.response_tg.json
