import json
from urllib.parse import unquote

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from webpagecapture import generate_webpage_screenshot

webserver = FastAPI()
webserver.mount(
    path="/screenshots",
    app=StaticFiles(directory=f"/app/screenshots/"),
    name="screenshots"
)


@webserver.get("/")
async def hello_world():
    return {"message": "Hello World"}


@webserver.post("/")
async def get_page_screenshot(request: Request):
    if request.headers.get("Content-Type") == "application/json":
        json_payload = await request.json()
        page_url = json_payload.get("page_url")

        if page_url is not None:
            page_url = unquote(page_url)
            success, extra_data = await generate_webpage_screenshot(page_url)

            if not success:
                return Response(
                    status_code=500,
                    headers={"Content-Type": "application/json"},
                    content=json.dumps({"error": f"Internal Server Error. {extra_data}"}))

            screenshot_url = str(request.url) + f"screenshots/{extra_data}"
            screenshot_url = screenshot_url.replace("http", "https")
            return Response(
                status_code=200,
                content=json.dumps({"screenshot_url": screenshot_url}))
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            content=json.dumps({"error": "page_url is required"}))
    return Response(
        status_code=400,
        headers={"Content-Type": "application/json"},
        content=json.dumps({"error": "Invalid request"}))
