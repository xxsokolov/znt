from __future__ import annotations
import uvicorn
from fastapi import FastAPI, status
from classes.logger import Log
from pydantic import BaseModel, Field


class sendMessage(BaseModel):
    chat_id: str = Field(default="", title='Chat ID', description="Укажите @username или Chat Name", include_in_schema=True)
    text: str = Field(default="", title='Text', description="The description of the item", max_length=300)
    disable_web_page_preview: bool = False
    disable_notification: bool = False


class FileItemBase(BaseModel):
    current_project: str = "Test project"


api = FastAPI(debug=True)
v1 = FastAPI(debug=True)
api.mount("/api/v1", v1)

logger = Log(True).log


def run(host="0.0.0.0", port=80):
    return uvicorn.run(api, host=host, port=port)


@v1.post("/telegram/sendMessage", status_code=status.HTTP_202_ACCEPTED)
def read_item(item: sendMessage):
    logger.info('cool')
    return item

# znt = FastAPI()
# v1 = FastAPI()
#
# # @znt.on_event('startup')
# # def startup():
# #     logger = Log(True).log
# #     bot_config = ReadYaml(logger=logger, path='../.bots.yaml').read_bots_yaml()
#
# @v1.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     xxx = 2
#     return {"item_id": item_id, "q": q}
#
# znt.mount("/api/v1", v1)
# if __name__ == "__main__":
#     uvicorn.run("__main__:znt", host="0.0.0.0", port=8000, reload=True, workers=1)
# # uvicorn main:app --reload
