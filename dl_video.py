import requests
from bs4 import BeautifulSoup
from os import getcwd, listdir
from sys import argv
import html5lib
from my_user_info import user_info
from utils import create_dir, display_message, COLORS


def get_mp4_link(video_tag):
    '''Returns a link that ends with '.mp4' if any by iterating on the contents
    of <video> tag'''
    for content in video_tag:
        if content != '\n' and 'SD' in content.attrs.values():
            return content['src']
    return None


def download_video(link: str, path: str) -> None:
    file_name = link.split('/')[-1]
    if file_name in listdir(path):
        print(f"{COLORS['WARNING']}Video {file_name} already exists{COLORS['ENDC']}")
        return
    req_download = requests.get(link, stream=True)
    with open(path + '/' + file_name, 'wb') as f:
        print("Downloading video "
                f"{COLORS['OKBLUE']}{file_name}{COLORS['ENDC']}...")
        for chunk in req_download.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    print("Video "
        f"{COLORS['OKBLUE']}{file_name}{COLORS['ENDC']} finished downloading")


def get_auth_token(session: requests.Session, login_link: str) -> str:
    get_req = session.get(login_link)
    soup = BeautifulSoup(get_req.content, 'html5lib')
    auth_token = soup.find("input", {"name": "authenticity_token"}).get('value')
    return auth_token


def check_login(login_response: requests.Response) -> bool:
    soup = BeautifulSoup(login_response.content, 'html5lib')
    logged_in_attribute = soup.find_all("span", attrs={'data-login':'nammari'})
    if logged_in_attribute:
        return True
    return False


def scrap_intranet(payload: dict, login_link: str, elearning_link: str) -> None:
    with requests.Session() as session:
        payload['authenticity_token'] = get_auth_token(session, login_link)
        login_response = session.post(login_link, data=payload)
        if check_login(login_response) is False:
            display_message(login_link, 'FAIL')
            return
        display_message(login_link, 'SUCCESS')
        elearning_response = session.get(elearning_link)
        find_videos(session, elearning_response, getcwd())


def get_links(soup, filters: dict):
    '''returns a list of links who's parent html attributes match filters'''
    links = []
    all_links = soup.find_all(attrs=filters)
    if not all_links:
        return []
    children = all_links[0].findChildren()
    for child in children:
        if 'href' in child.attrs.keys():
            links.append(INTRA_PREFIX_LINK + child['href'])
    return links


def find_videos(session: requests.Session, req: requests.Response, path: str):
    '''Recursively searches for links whos attributes or parents attributes
    match the filter argument then creates a directory and downloads the video
    associated whith each link'''
    soup = BeautifulSoup(req.content, 'html5lib')
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


if __name__ == "__main__":
    E_LEARNING_LINK = "https://elearning.intra.42.fr/tags/38/notions"
    INTRA_PREFIX_LINK = "https://elearning.intra.42.fr"
    LOGIN_LINK = "https://signin.intra.42.fr/users/sign_in"
    USER_NAME = input("Please enter your 42 user_name: ")
    USER_PASSWORD = input("Please enter your 42 password: ")
    USER_LINK = input(
        "Please enter the link to the page you want to "
        f"scrap. Otherwise click 'enter' to defautl to: \n{E_LEARNING_LINK}")
    if not USER_LINK:
        USER_LINK = E_LEARNING_LINK
    login_payload = {
        "user[login]": USER_NAME,
        "user[password]": USER_PASSWORD,
        "commit": 'Sign in',
        "authenticity_token": None
    }
    scrap_intranet(login_payload, LOGIN_LINK, USER_LINK)
