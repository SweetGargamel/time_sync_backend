from typing import Callable, Any
import base64
from Crypto.Cipher import AES
from dataclasses import dataclass
import aiohttp
from bs4 import BeautifulSoup

def encrypt(password: str, salt: str) -> str:
    iv = b'a' * 16
    cipher = AES.new(salt.encode(), AES.MODE_CBC, iv)
    data = ('a' * 64 + password).encode()
    # PKCS7 padding
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len]) * pad_len
    ct = cipher.encrypt(data)
    return base64.b64encode(ct).decode()

def extract_context(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, 'html.parser')
    form = soup.find(id='casLoginForm')
    if not form:
        return None
    
    context = {}
    for input_tag in form.find_all('input', type='hidden'):
        name = input_tag.get('name')
        if name:
            context[name] = input_tag.get('value', '')
        else:
            id_attr = input_tag.get('id')
            if id_attr:
                context[id_attr] = input_tag.get('value', '')
    return context

@dataclass
class LoginCredential:
    castgc: str

    @classmethod
    async def from_login(cls, username: str, password: str, captcha_cb: Callable[[bytes], Any]) -> 'LoginCredential':
        login_op_start = await LoginOperation.start()
        if not isinstance(login_op_start, LoginOperation.WaitingVerificationCode):
            raise RuntimeError("LoginOperation is not WaitingForVerificationCode after start()")
        
        captcha_answer = await captcha_cb(login_op_start.captcha)
        login_op = await login_op_start.finish(username, password, captcha_answer)
        
        if not isinstance(login_op, LoginOperation.Done):
            raise RuntimeError("LoginOperation did not done after finish()")
        return login_op.credential

class LoginOperation:
    class WaitingVerificationCode:
        def __init__(self, session, captcha: bytes, context: dict):
            self.session = session
            self.captcha = captcha
            self.context = context

        async def finish(self, username: str, password: str, captcha_answer: str) -> 'LoginOperation.Done':
            try:
                encrypted_password = encrypt(password, self.context['pwdDefaultEncryptSalt'])
                
                form = self.context.copy()
                form.update({
                    'username': username,
                    'password': encrypted_password,
                    'captchaResponse': captcha_answer,
                    'ddlt':'userNamePasswordLogin'
                })

                async with self.session.post('https://authserver.nju.edu.cn/authserver/login', data=form) as resp:
                    for cookie in self.session.cookie_jar:
                        if cookie.key == 'CASTGC':
                            return LoginOperation.Done(LoginCredential(cookie.value))
                    
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    msg = soup.find(id='msg')
                    if msg:
                        raise ValueError(msg.text.strip())
                    raise ValueError("No CASTGC, cannot load reason")
            finally:
                await self.session.close()

    class Done:
        def __init__(self, credential: LoginCredential):
            self.credential = credential

    @staticmethod
    async def start() -> WaitingVerificationCode:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
            'origin': 'https://authserver.nju.edu.cn',
            'referer': 'https://authserver.nju.edu.cn/authserver/login'
        }
        
        session = aiohttp.ClientSession(headers=headers)
        
        try:
            async with session.get('https://authserver.nju.edu.cn/authserver/login') as resp:
                html = await resp.text()
                context = extract_context(html)
                if not context:
                    raise ValueError("Failed to extract login context")

            async with session.get('https://authserver.nju.edu.cn/authserver/captcha.html') as resp:
                captcha = await resp.read()

            return LoginOperation.WaitingVerificationCode(session, captcha, context)
        except Exception:
            await session.close()
            raise