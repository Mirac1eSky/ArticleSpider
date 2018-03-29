
import re

def get_salary(value):
    x = re.findall(r'(?:\d+)+',value)
    if x:
        minsalary = x[0]
        maxsalary = x[1]
        return minsalary,maxsalary
    else:
        pass
        return 0
if __name__ == "__main__":
    print(get_salary("100k-500k"))