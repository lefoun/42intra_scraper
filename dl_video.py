import requests
from bs4 import BeautifulSoup
import os
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
    if file_name in os.listdir(path):
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


def scrap_intranet(payload: dict, login_link: str) -> None:
    with requests.Session() as session:
        payload['authenticity_token'] = get_auth_token(session)
        login_response = session.post(login_link, data=payload)
        print(login_response.status_code)
        if login_response.status_code != 200:
            print(f"{COLORS['FAIL']}")
            print(f"Login attempt to {login_link} failed")
            print(f"{COLORS['ENDC']}")
            return
        elearning_response = session.get(E_LEARNING_LINK)
        find_videos(session, elearning_response, DOWNLOAD_DIR)


#def get_links(soup, ):
    #all_links = soup.find_all(lambda tag: 'class' in tag.attrs and 
                #("notion-grid" in tag.attrs['class'] 
                #or "subnotion-grid" in tag.attrs['class']))
    #if not all_links:
        #return []
    #links = []
    #children = all_links[0].findChildren()
    #for child in children:
        #if 'href' in child.attrs.keys():
            #links.append(INTRA_PREFIX_LINK + child['href'])
    #return links


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


if __name__ == "__main__":
    INTRA_PREFIX_LINK = "https://elearning.intra.42.fr"
    E_LEARNING_LINK = "https://elearning.intra.42.fr/tags/38/notions"
    LOGIN_LINK = "https://signin.intra.42.fr/users/sign_in"
    DOWNLOAD_DIR = os.getcwd()
    login_payload = {
        "user[login]": user_info['login'],
        "user[password]": user_info['password'],
        "commit": 'Sign in',
        "authenticity_token": None
    }
    scrap_intranet(login_payload, LOGIN_LINK)
