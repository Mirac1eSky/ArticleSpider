import hashlib
import datetime
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    else:
        print("*" *50)
        print("NOT URL")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def dateconvert(time):
    try:
        time = time.strip().replace("·", "").strip()
        math = re.match(".\d{4}\d{2}\d{2}",time)
        # if math:
        #     time = math.group(1).strip("")
        #     print(time)
        date = datetime.datetime.strptime(time,"%Y/%m/%d").date()
        #print(date)
    except Exception as e:
        date = datetime.datetime.now().date()
    return date

def extract_nums(text):
    #提取数字
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

def get_salary(value):
    x = re.findall(r'(?:\d+)+',value)
    if x:
        minsalary = int(x[0])*1000
        maxsalary = int(x[1])*1000
        return minsalary,maxsalary
    else:

        return 0,0


def get_experience(value): #获取经验年限
    x = re.findall(r'(?:\d+)+',value)
    if x:
        minyear = int(x[0])
        maxyear = int(x[1])
        return minyear,maxyear
    else:
        return 0,0


def handle_data(value):
    b_time = ""
    time = datetime.datetime.now()
    string = dateconvert(time)
    match = re.match(r"^\d+天",value)
    match1 = re.match(r"^\d+:\d+",value)
    match2 = re.match(r"^\d+-\d+-\d+",value)
    if match:
        current_day = string.day  # 获取当前日期的天
        print(current_day)
        day = match.group()
        d = re.match(r"^\d+", day)
        print(d.group())
        day = current_day - int(d.group())
        b_time = string.replace(day=day)
        #print(b_time)
        return b_time
    elif match1:
        return string

    elif match2:
        return match2.group()
    else:
        return 0

if __name__ == "__main__":
    print(handle_data("2018-01-01  发布于拉勾网"))