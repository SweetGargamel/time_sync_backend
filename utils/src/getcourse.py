from datetime import datetime, date,timezone
import aiohttp
from typing import Optional
from .login import LoginCredential

async def build_client(auth: LoginCredential) -> aiohttp.ClientSession:
    cookies = {
        'CASTGC': auth.castgc
    }
    
    # 创建带有禁用 SSL 验证的 session
    connector = aiohttp.TCPConnector(ssl=False)
    session = aiohttp.ClientSession(
        cookies=cookies,
        headers={
            'User-Agent': 'rust-reqwest/0.11.18'
        },
        connector=connector
    )
    return session

async def get_course_raw(auth: LoginCredential) -> str:
    async with await build_client(auth) as client:
        # Get necessary cookies
        await client.get('https://ehall.nju.edu.cn/appShow?appId=4770397878132218')
        
        # Get latest semester
        async with client.post(
            'https://ehallapp.nju.edu.cn/jwapp/sys/wdkb/modules/jshkcb/dqxnxq.do'
        ) as resp:
            semesters = await resp.json()
            try:
                latest_semester = semesters['datas']['dqxnxq']['rows'][0]['DM']
            except (KeyError, IndexError):
                raise ValueError("Cannot resolve the latest semester")

        # Get course data
        form = {
            'XNXQDM': latest_semester,
            'pageSize': '9999',
            'pageNumber': '1'
        }
        async with client.post(
            'https://ehallapp.nju.edu.cn/jwapp/sys/wdkb/modules/xskcb/cxxszhxqkb.do',
            data=form
        ) as resp:
            text =await resp.text()
            # print(text)
            return text

def parse_semester_info(info: dict) -> Optional[date]:
    try:
        date_str = info['XQKSRQ'].split()[0]  # "2025-02-17 00:00:00" -> "2025-02-17"
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (KeyError, ValueError):
        return None

async def get_first_week_start(auth: LoginCredential) -> date:
    async with await build_client(auth) as client:
        # Get necessary cookies
        await client.get('https://ehall.nju.edu.cn/appShow?appId=4770397878132218')
        
        # Get semester info
        async with client.get(
            'https://ehallapp.nju.edu.cn/jwapp/sys/wdkb/modules/jshkcb/cxjcs.do'
        ) as resp:
            semester_info = await resp.json()
        try:
            rows = semester_info['datas']['cxjcs']['rows']
        except KeyError:
            raise ValueError("Semester info not array")

        current_date = datetime.now(timezone.utc).date()
        
        # Find the most recent past semester start
        for row in rows:
            semester_start = parse_semester_info(row)
            if semester_start:
                if (current_date - semester_start).total_seconds() > 0:
                    return semester_start
                    
        raise ValueError(f"No semester start found, semester info: {semester_info}")