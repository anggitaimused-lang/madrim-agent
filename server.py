import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

# 1. Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="Madrim AI Agent & UI Skills MCP Bridge",
    description="Server lokal terintegrasi untuk Generative UI & Model Context Protocol"
)

# 2. Struktur Format Request
class PromptRequest(BaseModel):
    prompt: str

# 3. Setup Gemini & Madrim Persona
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    pass 

try:
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
except Exception as e:
    print("⚠️ API Key belum terpasang dengan benar.")

system_instruction = """Kamu adalah Madrim, AI Agent ahli arsitektur sistem, pengembangan kode, dan desain visual UI/UX.
Tugas utamamu adalah menerjemahkan ide menjadi spesifikasi teknis, struktur database, dan kode yang efisien.
Dalam merancang panduan antarmuka, selalu prioritaskan clean executive UI, struktur layout Bento grid, dan tipografi Plus Jakarta Sans. Gunakan palet warna Navy Blue (#0033CC) sebagai fondasi utama dan Orange (#F97316) sebagai aksen.
Berikan respons yang terstruktur, langsung ke poin teknis, dan siap dieksekusi."""

ui_generation_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="execute_ui_generation",
            description="Mengirimkan parameter spesifikasi UI ke sistem perender visual eksternal.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "component_type": types.Schema(type=types.Type.STRING, description="Jenis antarmuka, misal: bento_card, dashboard_header"),
                    "color_palette": types.Schema(type=types.Type.STRING, description="Kode hex warna primer dan aksen"),
                    "data_variables": types.Schema(type=types.Type.STRING, description="Variabel data yang akan diikat"),
                },
                required=["component_type", "color_palette"]
            )
        )
    ]
)

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    tools=[ui_generation_tool],
    temperature=0.3,
)

# 4. Endpoint Utama Generasi UI
@app.post("/generate-ui")
async def generate_ui(request: PromptRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key belum terpasang di server.")

    try:
        chat = client.chats.create(model="gemini-3.5-flash-lite", config=config)
        response = chat.send_message(request.prompt)
        
        if response.function_calls:
            for fn in response.function_calls:
                if fn.name == "execute_ui_generation":
                    return {
                        "status": "success",
                        "type": "ui_component",
                        "data": fn.args
                    }
                    
        if response.text:
            return {
                "status": "success", 
                "type": "text", 
                "message": response.text
            }
            
        raise HTTPException(status_code=500, detail="Madrim tidak merespons dengan format yang dikenali.")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan server AI: {str(e)}")

# 5. Endpoint Katalog Skills (Menyesuaikan standar UI Skills MCP)
@app.get("/skills")
async def list_skills():
    """
    Mengembalikan daftar keterampilan (skills) Bento Grid & Clean Executive UI yang dikuasai Madrim.
    """
    return {
        "status": "success",
        "count": 3,
        "skills": [
            {
                "slug": "clean-executive-dashboard",
                "name": "Clean Executive Dashboard UI",
                "description": "Merancang tata letak header dan statistik eksekutif dengan palet Navy Blue & Orange."
            },
            {
                "slug": "bento-grid-hr",
                "name": "Bento Grid HR & KPI Card",
                "description": "Struktur kartu modular untuk metrik kinerja karyawan, retensi, dan rekrutmen."
            },
            {
                "slug": "system-architecture-spec",
                "name": "System Architecture & JSON Spec",
                "description": "Menerjemahkan kebutuhan bisnis menjadi parameter JSON dan arsitektur kode siap eksekusi."
            }
        ]
    }

# 6. Endpoint Manifest MCP Utama
@app.get("/mcp/manifest")
async def mcp_manifest():
    return {
        "mcp_version": "1.0.0",
        "server_name": "Madrim-Generative-UI-Server",
        "tools": [
            {
                "name": "execute_ui_generation",
                "description": "Menghasilkan spesifikasi desain Clean Executive UI & Bento Grid berbasis AI.",
                "endpoint": "/generate-ui"
            },
            {
                "name": "list_skills",
                "description": "Melihat daftar pustaka skill tata letak UI yang tersedia di server Madrim.",
                "endpoint": "/skills"
            }
        ]
    }

# 7. Blok Eksekusi Uvicorn
if __name__ == "__main__":
    print("🚀 Menyalakan Server Madrim API & UI Skills MCP Bridge di port 8000...")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)