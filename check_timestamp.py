import datetime

timestamp = 1754128800
dt = datetime.datetime.fromtimestamp(timestamp)
print(f'타임스탬프 {timestamp} = {dt}')
print(f'날짜: {dt.strftime("%Y-%m-%d")}')
print(f'시간: {dt.strftime("%H:%M:%S")}')

# 2025-08-02 19:00:00의 타임스탬프도 계산해보기
target_time = datetime.datetime.strptime("2025-08-02 19:00:00", "%Y-%m-%d %H:%M:%S")
target_timestamp = int(target_time.timestamp())
print(f'\n2025-08-02 19:00:00 = 타임스탬프 {target_timestamp}')

# 비교
print(f'\n비교:')
print(f'숨겨진 데이터: {timestamp}')
print(f'19:00 타임스탬프: {target_timestamp}')
print(f'일치 여부: {timestamp == target_timestamp}')