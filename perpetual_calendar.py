import calendar


def main():
    print("\n萬年曆查詢系統")
    try:
        year = int(input("請輸入年份 (例如 2023): "))
        month = int(input("請輸入月份 (1-12): "))
    except ValueError:
        print("輸入格式錯誤")
        return

    if month < 1 or month > 12:
        print("月份必須在1到12之間")
        return

    # 顯示指定月份的日曆
    print(f"\n{year} 年 {month} 月日曆:")
    print(calendar.month(year, month))

    try:
        day = int(input("若要查詢某日的星期，請輸入日期 (1-31)，或輸入 0 跳過: "))
    except ValueError:
        print("輸入格式錯誤")
        return

    if day:
        try:
            weekday = calendar.weekday(year, month, day)
        except calendar.IllegalMonthError:
            print("月份不正確")
            return
        except ValueError:
            print("日期不正確")
            return

        week_names = ['星期一','星期二','星期三','星期四','星期五','星期六','星期日']
        print(f"{year}年{month}月{day}日是{week_names[weekday]}")


if __name__ == "__main__":
    main()
