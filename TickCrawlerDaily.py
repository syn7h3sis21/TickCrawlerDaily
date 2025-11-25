import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
import os
import polars as pl
import requests
import shutil
import time
from tqdm import tqdm
from zipfile import ZipFile

import ujson

class TickCrawlerDaily:
    def __init__(self):
        with open('./config.json', 'r') as f:
            config = ujson.load(f)
            
        self.inst_id = config['inst_id']
        self.start_utc8 = config['start_utc8']
        self.end_utc8 = config['end_utc8']

        self.MAX_TIMEOUT = 3

    def download_and_extract_zip(self, url: str, csv_path: str):
        if os.path.exists(csv_path):
            print(f'CSV file {csv_path} already exists, using local file.')
            return csv_path

        # print(f'Downloading ZIP file from {url}')
        temp_zip_path = f'./temp/{csv_path[:-4]}.zip'
        try:
            # resp = requests.head(url)
            # total_size = int(resp.headers.get('content-length', 0))

            resp = requests.get(url)
            with open(temp_zip_path, 'wb') as f:
                f.write(resp.content)
            with ZipFile(temp_zip_path) as z:
                z.extractall(f'./daily/{self.inst_id}/')
            os.remove(temp_zip_path)
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f'CSV file {csv_path} not found in ZIP')
        except Exception as e:
            raise Exception(f'Failed to download or extract ZIP: {e}')

    def manage_download_csv(self, file_date: date):
        csv_path = f'./daily/{self.inst_id}/{self.inst_id}-trades-{file_date}.csv'
        while True:
            if not os.path.exists(csv_path):
                url = (
                    f'https://www.okx.com/cdn/okex/traderecords/trades/daily/'
                    + f'{file_date.strftime('%Y%m%d')}/{self.inst_id}-trades-{file_date}.zip'
                )
                # print(f'\nDownloading required tick data for {file_date}')
                try:
                    self.download_and_extract_zip(url, f'{self.inst_id}-trades-{file_date}')
                except Exception as e:
                    print(f'Failed to manage tick data for {file_date}: {e}')
            else:
                df = pl.read_csv(csv_path, encoding='GB2312')
                if 'trade_id/撮合id' in df.columns:
                    df = df.rename({
                        'trade_id/撮合id': 'trade_id',
                        'side/交易方向': 'side',
                        'size/数量': 'size',
                        'price/价格': 'price',
                        'created_time/成交时间': 'created_time'
                    })
                else:
                    df = pl.read_csv(csv_path, encoding='utf-8')
                    df = df.drop('instrument_name')
                df.write_csv(csv_path)
                break

    def run(self):
        dt_start = datetime.strptime(self.start_utc8, '%Y-%m-%d').date()
        dt_end = datetime.strptime(self.end_utc8, '%Y-%m-%d').date()
        os.makedirs(f'./daily/{self.inst_id}', exist_ok=True)
        os.makedirs('./temp', exist_ok=True)

        for i in tqdm(range((dt_end - dt_start).days + 1),
                      total=(dt_end - dt_start).days,
                      desc='Downlaoding required ticks data',
                      leave=False):
            if f'{self.inst_id}-trades-{dt_start + timedelta(days=i)}.csv' not in os.listdir(f'./daily/{self.inst_id}/'):
                self.manage_download_csv(dt_start + timedelta(days=i))

        # with ThreadPoolExecutor(max_workers=8) as executor:
        #     res = tqdm(
        #         executor.map(
        #             self.manage_download_csv,
        #             [dt_start + timedelta(days=i) for i in range((dt_end - dt_start).days + 1)
        #              if f'{self.inst_id}-trades-{dt_start + timedelta(days=i)}.csv' not in os.listdir(f'./daily/{self.inst_id}/')]
        #         ),
        #         total=(dt_end - dt_start).days,
        #         desc='Downlaoding required ticks data',
        #         leave=False
        #     )
        # print(res)

        shutil.rmtree('./temp')
        print('Download\'s complete.')


if __name__ == '__main__':
    TickCrawlerDaily().run()
