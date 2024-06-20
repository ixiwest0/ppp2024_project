import pandas as pd
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt

#분석 데이터
def analytical_data(df):
    return df.groupby(df['year']).agg({'tmax': 'max', 'tmin': 'min', 'tdiff': 'max', 'rainfall': 'max'})

#2023 최고기온 데이터
def tmax_2023(df):
    df_2023 = df[df['year'] == 2023]
    tmax_2023 = df_2023['tmax']
    return pd.DataFrame(tmax_2023)
    

def main():
    url = "https://api.taegon.kr/stations/146/?sy=2013&ey=2023&format=html"
    filename = "./weather_146_2013-2023.xlsx"


    #크롤링을 통해 데이터 받아와서 엑셀에 저장하기
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    data = soup.table.find("tbody").find_all("tr")

    data_list = []

    for value in data:
        items = value.find_all("td")
        data_row = [float(item.get_text(strip=True)) for item in items]
        data_list.append(data_row)

    header = soup.table.find("thead").find_all("td")
    col = [item.get_text(strip=True) for item in header]

    df = pd.DataFrame(data_list, index =range(1, len(data_list)+1) , columns=col)

    #일교차 구하기
    df['tdiff'] = df['tmax'] - df['tmin']

    #연도 별 최고기온 구하기
    df_year_analytisis = analytical_data(df)

    #2023년 최고기온 데이터
    df_tmax_2023 = tmax_2023(df)

    #분석한 데이터를 이용한 시각 데이터 만들기
    plt.rcParams['font.family'] = ['AppleGothic', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

    #tmax 선 그래프
    df_tmax = df_year_analytisis.loc[:,['tmax']]
    df_tmax.plot(color = "r")
    plt.savefig('tmax_graph.png')

    #tmin 선그래프
    df_tmin = df_year_analytisis.loc[:,['tmin']]
    df_tmin.plot(color = "b")
    plt.savefig('tmin_graph.png')

    #rainfall 강수량 그래프
    df_rainfall = df_year_analytisis.loc[:,['rainfall']]
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.bar(df_rainfall.index, df_rainfall['rainfall'])
    fig.savefig('max_rainfall.png')

    #2023 최고기온 양상
    df_tmax_2023.plot(color = "r")
    plt.savefig("tmax_2023.png")

    #2개의 데이터를 한 엑셀 파일의 각각 다른 시트에 저장
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name='weather_db')
        df_year_analytisis.to_excel(writer, sheet_name='analysis_db')
        df_tmax_2023.to_excel(writer, sheet_name= "2023_tmax_db")

        #analsis_db의 이미지
        worksheet = writer.sheets['analysis_db']
        worksheet.insert_image('G2', 'tmax_graph.png')
        worksheet.insert_image('S2', 'tmin_graph.png')
        worksheet.insert_image('G27', 'max_rainfall.png')

        #2023_tmax_db의 이미지
        worksheet = writer.sheets['2023_tmax_db']
        worksheet.insert_image('E2', 'tmax_2023.png')

if __name__ == "__main__":
    main()