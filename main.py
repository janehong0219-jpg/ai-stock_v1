from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import etf_service  # 匯入剛剛確認過的廚房

app = FastAPI()

# 允許跨域 (讓 Vue 可以連線)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定義資料格式：現在只收一個 symbol 字串
class StockRequest(BaseModel):
    symbol: str

@app.get("/")
def read_root():
    return {"message": "AI 投顧伺服器運作中"}

@app.post("/api/analyze")
def analyze_stock_endpoint(request: StockRequest):
    print(f"收到分析請求: {request.symbol}")
    # 呼叫 etf_service 裡面的 analyze_stock 函式
    data = etf_service.analyze_stock(request.symbol)
    return data