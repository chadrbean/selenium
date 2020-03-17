from selenium import webdriver
import traceback
import re
import subprocess
import youtube_dl
import os
import time
import sys


EXE_PATH = '/bin/chromedriver'
driver = webdriver.Chrome(executable_path=EXE_PATH)
driver.get('https://app.site.com/dashboard')
skip_videos = int(input("What video number do you want to start at for first video only (default 0): ")) # Can be used if you dont want to start from the begining... default is 0
login_username = input("Enter Your Username")
login_password = input("Enter Your Password: ")


def login():
    # Login To Website
    time.sleep(5)
    driver.find_element_by_name("username").send_keys(login_username)
    driver.find_element_by_name("password").send_keys(login_password)
    login_button = driver.find_element_by_xpath("/html/body/div/div/div[2]/form/div/div/button")
    login_button.click()
    time.sleep(10)
    course_links = ["https://site.com/cp/modules/view/id/181"]
    driver.get(course_links[0])
    driver.get("https://linuxacademy.com/cp/ssologin#")
    time.sleep(20)

# Function to Download Videos
error_links = []
def download_videos():
    course_count = 100
    course_count = course_count + skip_videos
    video_links = []
    # Make a dir for files from title
    course_title = driver.find_elements_by_class_name("course-title")[0].text
    oscwd = "/run/media/chad/1TB/videos"
    try:
        os.chdir(oscwd)
        os.mkdir(course_title)
        os.chdir(course_title)
    except:
        os.chdir(course_title)
    for i in driver.find_elements_by_xpath("//*[@id='syllabus']/a"):
        if "hands" not in i.get_attribute("href") and "challenge" not in i.get_attribute("href") and "quiz" not in i.get_attribute("href") and "exercise" not in i.get_attribute("href"):
            video_links.append(i.get_attribute("href"))
    for i in video_links[skip_videos:]:
        try:
            driver.get(i)
            driver.implicitly_wait(15)
            title_text = driver.find_elements_by_class_name("video-header h2")[0].text
            title_text = title_text.replace("Lecture:", "")
            title_text = title_text.replace("\\", "")
            title_text = title_text.replace("/", "")
            # Contains the url for the video
            script_text = driver.find_element_by_tag_name("head").get_attribute("innerText")
            try:
                find_url = re.search(r".video-cdn.*.,\"track", script_text)
                final_url = "https:/" + find_url.group(0)[:-8]
                final_url = final_url.replace("\\", "")
            except:
                find_url = re.search(r".video-cdn.*.,\"image", script_text)
                final_url = "https:/" + find_url.group(0)[:-8]
                final_url = final_url.replace("\\", "")
            
            print("youtube-dl", "-o{} - {}.mp4".format(course_count, title_text), final_url)
            subprocess.run(["youtube-dl", "-o{} - {}.mp4".format(course_count, title_text), final_url])
            course_count += 1
            driver.execute_script("window.history.go(-1)")
            driver.implicitly_wait(30)
        except Exception:
            error_links.append([i,title_text, final_url])
            break


# Loop text file and Loop through courses and call function to download videos
def loop_courses():
    course_links = []
    with open("course_urls_newline.txt", "r") as fr:
        for i in fr:
            course_links.append(i)
    for i in course_links:
        driver.get(i)   
        driver.implicitly_wait(10)
        download_videos()


login()
loop_courses()
print(error_links)
