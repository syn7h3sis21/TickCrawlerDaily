# TickCrawlerDaily

简洁的 OKX 日线逐笔成交（tick/trades）下载工具。

## 功能
- 根据配置的交易对 (inst_id) 与日期区间，自动下载并解压 OKX 提供的每日成交记录 ZIP 文件。
- 支持不同编码（GB2312 / UTF-8）CSV 的兼容处理与统一输出。

## 依赖
- Python 3.8+
- Polars
- requests
- tqdm
- ujson

安装示例：
```
pip install -u polars requests tqdm ujson
```

## 配置 (config.json)
在项目根目录创建 `config.json`，示例：
```json
{
  "inst_id": "BTC-USD-SWAP",
  "start_utc8": "2024-01-01",
  "end_utc8": "2024-01-07"
}
```
字段说明：
- inst_id: OKX 的合约/交易对标识
- start_utc8 / end_utc8: 日期（格式 YYYY-MM-DD），使用北京时间（UTC+8）日期范围

## 运行
在项目目录下运行：
```
python TickCrawlerDaily.py
```
运行后：
- 临时文件保存在 `./temp`（脚本完成后会删除）
- 下载并解压后的 CSV 保存在 `./daily/{inst_id}/`

## 注意事项与常见问题
- 若已存在目标 CSV，脚本会复用本地文件以避免重复下载。
- 脚本尝试以 GB2312 编码读取 CSV，若列名不匹配则回退到 UTF-8 并去除 `instrument_name` 列。
- 请确保网络可访问 OKX CDN；若下载失败会打印错误信息并重试（脚本内可按需调整重试/超时策略）。
- 若遇解压或 CSV 列名问题，可手动检查 `./daily/{inst_id}/` 目录内文件以定位问题。

## 目录结构（简要）
- `TickCrawlerDaily.py`：主脚本
- `config.json`：配置文件（需手动创建）
- `./daily/{inst_id}/`：解压后的 CSV 存放目录
- `./temp`：临时 ZIP 存放（脚本执行完毕会删除）

## 许可证
MIT
