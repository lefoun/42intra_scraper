import requests
from bs4 import BeautifulSoup
from os import getcwd, listdir
from sys import argv
import html5lib
from my_user_info import user_info
from utils import create_dir, COLORS



def get_mp4_link(video_tag):
    for content in video_tag:
        if content != '\n' and 'SD' in content.attrs.values():
            return content['src']
    return None


def download_video(link: str, path: str) -> None:
    file_name = link.split('/')[-1]
    if file_name in listdir(path):
        print(f"Video {file_name} already exists in CWD")
        return
    req_download = requests.get(link, stream=True)
    with open(path + '/' + file_name, 'wb') as f:
        print(f"Downloading video {file_name}")
        for chunk in req_download.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    print(f"Video {file_name} finished downloading")


def get_auth_token(session: requests.Session) -> str:
    get_req = session.get(LOGIN_LINK)
    soup = BeautifulSoup(get_req.content, 'html5lib')
    auth_token = soup.find("input", {"name": "authenticity_token"}).get('value')
    return auth_token

def check_login(login_response: requests.Response) -> bool:
    soup = BeautifulSoup(login_response.content, 'html5lib')
    logged_in_attribute = soup.find_all("span", attrs={'data-login':'nammari'})
    if logged_in_attribute:
        return True
    return False


def display_message(link: str, status='FAIL'): 
    print(COLORS[status])
    print(f"Login {status} for address {link}.")
    print(f"{COLORS['ENDC']}")

def scrap_intranet(payload: dict, login_link: str, scrap_link: str) -> None:
    with requests.Session() as session:
        payload['authenticity_token'] = get_auth_token(session)
        login_response = session.post(login_link, data=payload)
        if check_login(login_response) is False:
            display_message(login_link, 'FAIL')
            return
        display_message(login_link, 'SUCCESS')
        elearning_response = session.get(scrap_link)
        find_videos(session, elearning_response, DOWNLOAD_DIR)


def get_links(soup, filter: dict):
    all_links = soup.find_all(attrs=filter)
    if not all_links:
        return []
    links = []
    children = all_links[0].findChildren()
    for child in children:
        if 'href' in child.attrs.keys():
            links.append(INTRA_PREFIX_LINK + child['href'])
    return links


def find_videos(session: requests.Session, get_req: requests.Response, path: str):
    soup = BeautifulSoup(get_req.content, 'html5lib')
    video_tag = soup.find("video")
    if video_tag:
        link = get_mp4_link(video_tag)
        create_dir(path)
        download_video(link, path)
    else:
        links = get_links(soup, {'class': ['notion-grid', 'subnotion-grid']})
        for link in links:
            req = session.get(link)
            find_videos(session, req, path + '/' + link.split('/')[-2])

string="this._user"
if __name__ == "__main__":
    E_LEARNING_LINK = "https://elearning.intra.42.fr/tags/38/notions"
    INTRA_PREFIX_LINK = "https://elearning.intra.42.fr"
    LOGIN_LINK = "https://signin.intra.42.fr/users/sign_in"
    user_name = input("Please enter your 42 user_name: ")
    #password = input("Please enter your 42 password: ")
    elearning_link = input(
        "Please enter the link to the page you want to "
        f"scrap. Otherwise click 'enter' to defautl to: \n{E_LEARNING_LINK}")
    DOWNLOAD_DIR = getcwd()
    if not elearning_link:
        elearning_link = E_LEARNING_LINK
    login_payload = {
        "user[login]": user_name,
        "user[password]": user_info['password'],
        "commit": 'Sign in',
        "authenticity_token": None
    }
    scrap_intranet(login_payload, LOGIN_LINK, elearning_link)
