def message(domain, uidb64, token):
    return f"아래 링크를 클릭하면 회원가입 인증이 완료됩니다. \n\n 회원가입 링크 : http://{domain}/activate/{uidb64}/{token}\n\n 감사합니다"


def find_message(domain, uidb64):
    return f"아래 링크를 클릭하면 비밀번호 변경이 이루어집니다. \n\n 비밀번호 변경 링크 : http://{domain}/change/{uidb64}\n\n 감사합니다"