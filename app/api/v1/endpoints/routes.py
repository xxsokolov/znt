from typing import Optional, NoReturn

from fastapi import APIRouter, status, UploadFile, File

from app import schemas
from app.services import (
    send_message
)

router = APIRouter()


@router.post("/telegram/sendMessage", status_code=status.HTTP_202_ACCEPTED, summary="Send message in Telegram")
async def telegram_send_message(data: schemas.SendMessage):
    # TODO: consider handling exception on unknown PEER_ID
    xxx = {'preferences': {
        "telegram":
            {"send":
                 {"bot": data.bot,
                  "chat_id": data.chat_id,
                  "charts": {
                      "title": data.title,
                      "period": data.period},
                  "message": {
                      "header": data.header,
                      "body": data.body}}},
        "zabbix":
            {"macros":
                 {"hostname": data.hostname, "itemid": data.itemid, "hostid": data.hostid, "triggerid": data.triggerid,
                  "triggerurl": data.triggerurl, "eventtags": data.eventtags, "eventid": data.eventid,
                  "actionid": data.actionid}},
        "znt":
            {"options":
                 {"graphs": data.graphs, "hostlinks": data.hostlinks, "graphlinks": data.graphlinks,
                  "acklinks": data.acklinks, "eventlinks": data.eventlinks, "triggerlinks": data.triggerlinks,
                  "eventtag": data.eventtag, "eventidtag": data.eventidtag, "itemidtag": data.itemidtag,
                  "triggeridtag": data.triggeridtag, "actionidtag": data.actionidtag, "hostidtag": data.hostidtag,
                  "zntsettingstag": data.zntsettingstag, "zntmentions": data.zntmentions, "keyboard": data.keyboard,
                  "graphs_period": data.graphs_period}}}}
    await send_message(xxx)
    return
