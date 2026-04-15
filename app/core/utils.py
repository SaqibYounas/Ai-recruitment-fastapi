import fitz  # PyMuPDF
import httpx

async def extract_text_from_url(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            doc = fitz.open(stream=response.content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    return None