from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import re
import copy

print("학교알리미 정보공시: 교과별(학년별) 평가계획 스크래핑 코드입니다")
print(r"(https://www.schoolinfo.go.kr/ei/ss/pneiss_a05_s1.do)")
year = input("연도 입력: ex)2023\n:")
semester = input("학기 입력: ex)1학기: '1'입력, 2학기: '2'입력\n:")
school_level = input("학교 입력: ex)고등학교\n:")
user_name = input("유저 이름 입력: ex)dong\n:")
folder_name = input("폴더 이름 입력: ex)원하는 폴더명\n:")


abs_path = os.path.dirname(os.path.abspath(__file__))
completed_school_names = list()
erred_school_names = list()
source_folder = f"/Users/{user_name}/Library/CloudStorage/Dropbox/sj/2023-2/연구/[진행중]학교평가계획 정보공시_chatgpt/{folder_name}"
    # "/Users/{user_name}/Documents/{folder_name}"

# 폴더가 이미 존재하는지 확인
if not os.path.exists(source_folder):
    try:
        os.makedirs(source_folder)
        print(f"폴더 '{source_folder}'가 생성되었습니다.")
    except OSError as e:
        print(f"폴더 생성에 실패했습니다: {e}")
else:
    print(f"폴더 '{source_folder}'는 이미 존재합니다.")

file_list = []
file_url_list = []

# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 불필요한 에러 메시지 없애기
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# 파일 다운로드 디렉토리 설정
prefs = {
    "download.default_directory": "/Users/{}/Documents/{}".format(user_name, folder_name),  # 다운로드하고자 하는 디렉토리 경로로 수정
    "download.prompt_for_download": False,
    "download.directory_upgrade": True
}
chrome_options.add_experimental_option("prefs", prefs)

# ChromeDriverManager를 통해 크롬 드라이버를 최신 버전 자동 설치하여 Service 만들어서 service에 저장한다
# try:
#     service = Service(executable_path=ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     print("True")
# except:
#     service = Service(executable_path=ChromeDriverManager(driver_version="114.0.5735.90").install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)

driver = webdriver.Chrome(options=chrome_options)
tmp_school_name = str()
tmp_succeeded_file_names=list()
tmp_file_name = str()
saved_file_log = list()
completed_si_names = list()
completed_gu_names = defaultdict(list)
while 1:
    try:
        driver.implicitly_wait(5)
        driver.get("https://www.schoolinfo.go.kr/ei/ss/pneiss_a05_s1.do")

        select_element = driver.find_element(By.ID, "gsYear")
        option_elements = select_element.find_elements(By.TAG_NAME, "option")

        for option in option_elements:
            if option.get_attribute("value") == year:
                option.click()
                break

        driver.find_element(By.CSS_SELECTOR, "#gsYearBtn").click()
        driver.find_element(By.CSS_SELECTOR,
                            "#searchForm > div > div > div.search_type.step5 > div.pws_tabs_container > div > ul > li:nth-child(6) > a").click()
        driver.find_element(By.CSS_SELECTOR,
                            "#gongsiTab > div.pws_tab_single.pws_hide.pws_show > div > ul > li:nth-child(1) > label > span").click()

        if school_level == "중학교":
            driver.find_element(By.XPATH, '//label[@for="hgJongryuGb_jung" and text()="중학교"]').click()
        elif school_level == "고등학교":
            driver.find_element(By.XPATH, '//label[@for="hgJongryuGb_go" and text()="고등학교"]').click()

        # 모든 경우의 수
        # 시 도 선택 경우의 수
        sido = driver.find_element(By.ID, "sidoCode")
        sido__elements = sido.find_elements(By.TAG_NAME, "option")


        # test
        # completed_si_names.append('서울특별시')
        # completed_gu_names['부산광역시'] += ['강서구']

        for i in sido__elements[1:]:
            si_name = i.text  # 서울특별시

            if si_name in completed_si_names:
                # 다 했으면 넘어가
                continue

            i.click()
            print(si_name, "클릭함")
            sigoongu = driver.find_element(By.ID, "sigunguCode")
            sigoongu__elements = sigoongu.find_elements(By.TAG_NAME, "option")


            for j in sigoongu__elements[1:]:
                gu_name = j.text  # 강동구
                if gu_name in completed_gu_names[si_name]:
                    # 다 했으면 넘어가
                    continue

                j.click()
                print(gu_name, "클릭함")

                file_list = []
                driver.find_element(By.CSS_SELECTOR, "#searchForm > input").click()  #검색버튼
                time.sleep(5)
                tbody = driver.find_elements(By.CSS_SELECTOR, '#contents > div > div > div.bbs-w > div > table > tbody')

                for tr in tbody:
                    option_elements = tr.find_elements(By.CSS_SELECTOR, '[id^="gongsiSelect"] option')
                    school_name_element = tr.find_elements(By.CSS_SELECTOR, 'td.col_schoolname')

                    # 폴더 미리 만들어놓는 코드
                    for _school_name in school_name_element:
                        """ if school_name.text[1:] == "성덕고등학교":
                            continue """
                        _school_name = _school_name.text[1:]
                        file_list.append(_school_name)  #file_list는 사실상 school_name_list
                        """ file.write(school_name+"\n") """


                    file_count = 0

                    # 본격 학교별로 다운로드 받는 코드
                    for option in option_elements:
                        if option.text == "교과별(학년별) 평가계획에 관한 사항":
                            option.click()  #"교과별(학년별) 평가계획에 관한 사항" 클릭
                            try:
                                txt = driver.find_element(By.CSS_SELECTOR, "#gongsiInfo > div.manager_info")
                                # 아예 제목만 있고 학교 정보가 없는 경우가 있는 경우 존재. 오류 남.
                                # print("이게 뭐길래", txt.text)
                                pattern = r"학교\s*:\s*([^|]+)"
                                match = re.search(pattern, txt.text)
                                school_name = match.group(1).strip()

                                tmp_school_name = copy.deepcopy(school_name)

                                succeeded_file_names = list()
                                etc_error_info = list()

                                if school_name in completed_school_names:
                                    print("{}는 이미 존재하므로 pass합니다".format(school_name))  #
                                    file_count += 1
                                    continue

                                print(school_name)

                                if school_name in erred_school_names:
                                    print("{}는 에러가 난 적이 있어 pass합니다".format(school_name))  #
                                    file_count += 1
                                    continue

                                # print(school_name, file_list[file_count], '이 두 개가 늘 같니??. 같을 걸로 예상')

                                # 학기 선택 도전 # fixing
                                # select_element = driver.find_element(By.ID, "gsYear")
                                select_semester = driver.find_element(By.ID, "select_trans_dt")
                                semester_elements = select_semester.find_elements(By.TAG_NAME, "option")
                                sm_checker = True
                                for sm_option in semester_elements:
                                    print("sm_option.get_attribute('value')", sm_option.get_attribute('value'))
                                    if semester == '2':
                                        if sm_option.get_attribute("value") == str(year) + str(3):
                                            print('okay')
                                            sm_option.click()
                                            time.sleep(1)
                                            break
                                    elif semester == '1':
                                        if sm_option.get_attribute("value") == str(year) + str(1):
                                            sm_option.click()
                                            time.sleep(1)
                                            break
                                    else:
                                        print('학기가 없는 것 같은데, 다음 학교로 가야겠다.')
                                        erred_school_names.append(file_list[file_count])
                                        saved_file_log.append([year,
                                                               semester,
                                                               school_level,
                                                               si_name,
                                                               gu_name,
                                                               file_list[file_count],
                                                               '',
                                                               '',
                                                               '학교 이름은 있으나 해당 학기가 없어영'
                                                               ])  # 2023, 고등학교, 서울특별시, 강남구, 성덕고등학교, [성공한 파일 목록], 에러난 파일명, 기타오류
                                        pd.DataFrame(saved_file_log, columns=['year',
                                              'semester',
                                              'school_level',
                                              'si', 'gun_gu',
                                              'school_name', 'succeeded_file',
                                              'errored_file_names', 'etc_error']).to_csv(source_folder + '/results.csv')
                                        file_count += 1
                                        sm_checker = False

                                if sm_checker == False:
                                    # file_count += 1 앞에서 해줬기 때문에 pass
                                    continue



                                try:
                                    print('붙임 파일을 다운로드 합니다...')
                                    print("year_t", type(year))
                                    print("sem_t", type(semester))
                                    if year == '2020' and semester == '2':
                                        print("맞네 이거네")
                                        attachments = driver.find_elements(By.CSS_SELECTOR,
                                                                           '#gongsiInfo > div.table_wrap > div.attached_file')
                                    else:
                                        attachments = driver.find_elements(By.CSS_SELECTOR,
                                                                           '#gongsiInfo > div.table_wrap > div:nth-child(3) > div.attached_file')
                                    # 아예 제목만 있고 붙임 파일 없는 경우가 있는 경우 존재. 오류 남.
                                    for attachment in attachments:
                                        file_name_elements = attachment.find_elements(By.CSS_SELECTOR, 'a.file_name')
                                        cnt = 1
                                        files_to_move = []
                                        for file_name_element in file_name_elements:
                                            # print(file_name_element.text)
                                            # print("파일 이름이 어쩧다고?", file_name_element.text)
                                            file_name = re.sub(r'(\.(hwp|pdf|zip|xlsx)).*$', r'\1', file_name_element.text,
                                                               flags=re.IGNORECASE)
                                            tmp_file_name = file_name
                                            print(cnt, file_name)
                                            files_to_move.append(file_name)  # 추후에 옮길 파일 파일명 리스트 저장

                                            # 첨부 파일 하나씩 눌러 다운로드!!!!!!!!!!!!!!!
                                            destination_folder = "/Users/{}/Documents/{}/{}/{}/{}".format(user_name,
                                                                                                          folder_name, si_name,
                                                                                                          gu_name,
                                                                                                          file_list[file_count])
                                            # print("destination_folder: ", destination_folder)

                                            if not os.path.exists(destination_folder):
                                                os.makedirs(destination_folder)
                                                # print("목적지 폴더 만듦!")

                                            params = {'behavior': 'allow', 'downloadPath': destination_folder}
                                            driver.execute_cdp_cmd('Page.setDownloadBehavior', params)

                                            file_name_element.click()
                                            succeeded_file_names.append(file_name)
                                            tmp_succeeded_file_names = copy.deepcopy(succeeded_file_names)
                                            cnt += 1

                                        # destination_folder = "/Users/{}/Documents/{}/{}/{}/{}".format(user_name, folder_name, si_name, gu_name, file_list[file_count])
                                        # print("destination_folder: ", destination_folder)
                                        #
                                        # if not os.path.exists(destination_folder):
                                        #     os.makedirs(destination_folder)
                                        #     print("목적지 폴더 만듦!")
                                        # time.sleep(2)  # 쉬었다가 해야(다운로드가 끝나야) 파일 옮겨짐.
                                        #
                                        # for _file in files_to_move:
                                        #     source_file_path = os.path.join(source_folder, _file)  #
                                        #     destination_file_path = os.path.join(destination_folder, _file)
                                        #     while os.path.exists(source_file_path) == False:
                                        #
                                        #         print(source_file_path, os.path.exists(source_file_path), "기다려!!")
                                        #         time.sleep(1)  # 파일 안생겼어? 기다려.--추가
                                        #
                                        #     if os.path.exists(source_file_path):
                                        #         shutil.move(source_file_path, destination_file_path)
                                        #         print(f"{_file}을(를) 이동했습니다.")
                                        #     else:
                                        #         etc_error_info.append(f"{_file} 파일 폴더로 옮기기 실패")
                                        #         print(f"{_file}을(를) 찾을 수 없습니다.")
                                        #
                                        # print("위 파일들을 {}에 저장 완료했습니다".format(file_list[file_count]))
                                        completed_school_names.append(file_list[file_count])
                                        # file = open("save.txt", "a")
                                        # file.write(file_list[file_count])
                                        # file.write("\n")
                                        # file.close()
                                        print()

                                        file_count += 1

                                    # 저장 성공했으므로 저장
                                    saved_file_log.append([year,
                                                           semester,
                                                           school_level,
                                                           si_name,
                                                           gu_name,
                                                           school_name,
                                                           succeeded_file_names,
                                                           '',
                                                           etc_error_info
                                                           ])  # 2023, 고등학교, 서울특별시, 강남구, 성덕고등학교, [성공한 파일 목록], 에러난 파일명, 기타오류
                                    pd.DataFrame(saved_file_log, columns=['year',
                                              'semester',
                                              'school_level',
                                              'si', 'gun_gu',
                                              'school_name', 'succeeded_file',
                                              'errored_file_names', 'etc_error']).to_csv(source_folder + '/results.csv')
                                except:
                                    # 아예 제목만 있고 붙임 파일이 없는 경우가 있는 경우 존재. 오류 남.
                                    erred_school_names.append(file_list[file_count])
                                    saved_file_log.append([year,
                                                           semester,
                                                           school_level,
                                                           si_name,
                                                           gu_name,
                                                           file_list[file_count],
                                                           '',
                                                           '',
                                                           '학교 이름은 있으나 알맹이가 없어영'
                                                           ])  # 2023, 고등학교, 서울특별시, 강남구, 성덕고등학교, [성공한 파일 목록], 에러난 파일명, 기타오류
                                    pd.DataFrame(saved_file_log, columns=['year',
                                              'semester',
                                              'school_level',
                                              'si', 'gun_gu',
                                              'school_name', 'succeeded_file',
                                              'errored_file_names', 'etc_error']).to_csv(source_folder + '/results.csv')
                                    file_count += 1

                            except:
                                erred_school_names.append(file_list[file_count])
                                saved_file_log.append([year,
                                                       semester,
                                                       school_level,
                                                       si_name,
                                                       gu_name,
                                                       file_list[file_count],
                                                       '',
                                                       '',
                                                       '학교 이름은 있으나 알맹이가 없어영'
                                                       ])  # 2023, 고등학교, 서울특별시, 강남구, 성덕고등학교, [성공한 파일 목록], 에러난 파일명, 기타오류
                                pd.DataFrame(saved_file_log, columns=['year',
                                              'semester',
                                              'school_level',
                                              'si', 'gun_gu',
                                              'school_name', 'succeeded_file',
                                              'errored_file_names', 'etc_error']).to_csv(source_folder + '/results.csv')
                                file_count += 1





                completed_gu_names[si_name] += [gu_name]

            completed_si_names.append(si_name)


    except Exception as e:
        erred_school_names.append(tmp_school_name)
        saved_file_log.append([year,
                               semester,
                               school_level,
                               si_name,
                               gu_name,
                               tmp_school_name,
                               tmp_succeeded_file_names,
                               tmp_file_name,
                               ''
                               ])  # 2023, 고등학교, 서울특별시, 강남구, 성덕고등학교, [성공한 파일 목록], 에러난 파일명, 기타오류
        pd.DataFrame(saved_file_log, columns=['year',
                                              'semester',
                                              'school_level',
                                              'si', 'gun_gu',
                                              'school_name', 'succeeded_file',
                                              'errored_file_names', 'etc_error']).to_csv(source_folder + '/results.csv')
        print("An error occurred:", str(e))

    finally:
        try:
            print()
            # file2.write(school_info)
            # file2.write("\n")
            # print("예외처리에 추가됩니다:", school_info)
            # file.close()
            # file2.close()
        except NameError:
            print("school_info is not defined or an error occurred before defining it.")





