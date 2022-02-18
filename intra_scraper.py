from os import getcwd, listdir
from sys import exit
from getpass import getpass
import requests
from bs4 import BeautifulSoup
from clint.textui import progress
from utils import create_dir, display_message, COLORS


def get_mp4_link(video_tag: BeautifulSoup, video_quality: str) -> str:
    """Returns a link that ends with '.mp4' (if any) by iterating
    on the contents of <video> tag
    """
    for content in video_tag:
        if content != "\n" and video_quality in content.attrs.values():
            return content["src"]
    return None


def download_video(link: str, path: str) -> None:
    """Downloads the video from [link] if it doesn't exist"""
    file_name = link.split("/")[-1]
    if file_name in listdir(path):
        print(f"{COLORS['WARNING']}Video {file_name} already exists{COLORS['ENDC']}")
        return
    req_download = requests.get(link, stream=True)
    with open(path + "/" + file_name, "wb") as file:
        total_length = int(req_download.headers.get("content-length"))
        print("Downloading video "
                f"{COLORS['OKBLUE']}{file_name}{COLORS['ENDC']}...")
        for chunk in progress.bar(req_download.iter_content(chunk_size=1024),
                                expected_size=total_length/(1024)):
            if chunk:
                file.write(chunk)
                file.flush()
    print("Video "
        f"{COLORS['OKBLUE']}{file_name}{COLORS['ENDC']} finished downloading")
    return


def get_auth_token(session: requests.Session, login_link: str) -> str:
    """Get the authenticity token required to login to 42 intranet"""
    response = session.get(login_link)
    soup = BeautifulSoup(response.content, "html5lib")
    auth_token = soup.find("input", {"name": "authenticity_token"}).get("value")
    return auth_token


def check_login(login_response: requests.Response, usr_name: str) -> bool:
    """Verify we are logged in"""
    soup = BeautifulSoup(login_response.content, "html5lib")
    logged_in_attribute = soup.find("span", attrs={"data-login": usr_name})
    if logged_in_attribute:
        return True
    return False


def get_links(soup, filters: dict) -> list:
    """Returns a list of links who's parent html attributes match filters"""
    links = []
    all_links = soup.find(attrs=filters)
    if all_links:
        children = all_links.findChildren()
        for child in children:
            if "href" in child.attrs.keys():
                links.append(INTRA_PREFIX_LINK + child["href"])
    return links


def find_videos(session: requests.Session, req: requests.Response, \
    path: str, video_quality: str) -> None:
    """Recursively searches for links whos attributes or parents attributes
    match the filter argument. Then downloads the videos if it found any.
    """
    soup = BeautifulSoup(req.content, "html5lib")
    video_tag = soup.find("video")
    if video_tag:
        link = get_mp4_link(video_tag, video_quality)
        create_dir(path)
        download_video(link, path)
    else:
        links = get_links(soup, {"class": ["notion-grid", "subnotion-grid"]})
        for link in links:
            req = session.get(link)
            find_videos(session, req, path + "/" + link.split("/")[-2], video_quality)


def scrap_intranet(payload: dict, login_link: str, elearning_link: str, \
    video_quality: str) -> None:
    with requests.Session() as session:
        payload["authenticity_token"] = get_auth_token(session, login_link)
        login_response = session.post(login_link, data=payload)
        login_successful = check_login(login_response, payload["user[login]"])
        if login_successful:
            display_message(login_link, "SUCCESS")
            elearning_response = session.get(elearning_link)
            find_videos(session, elearning_response, getcwd(), video_quality)
        else:
            display_message(login_link, "FAIL")


if __name__ == "__main__":
    E_LEARNING_LINK = "https://elearning.intra.42.fr/tags/38/notions"
    INTRA_PREFIX_LINK = "https://elearning.intra.42.fr"
    login_url = "https://signin.intra.42.fr/users/sign_in"
    user_name = input("Please enter your 42 user_name: ")
    user_password = getpass("\nPlease enter your 42 password(hidden): ")
    user_link = input(
        "\nPlease enter the link to the page you want to "
        f"scrap. Otherwise click 'enter' to defautl to:\n{E_LEARNING_LINK}")
    quality = input("\nDo you want to download the videos in SD or HD?"
               "\nEnter 'SD' for low quality or 'HD' for high: ")
    if not quality == 'HD' and not quality == 'SD':
        print("No such quality")
        exit()
    if not user_link:
        user_link = E_LEARNING_LINK
    login_payload = {
        "user[login]": user_name,
        "user[password]": user_password,
        "commit": 'Sign in',
        "authenticity_token": None
    }
    scrap_intranet(login_payload, login_url, user_link, quality)
    