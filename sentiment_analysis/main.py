import paddlehub as hub
import pandas as pd

def main():
    senta = hub.Module(name="senta_lstm")
    

    """
    sheet_num = 3
    sheet_name = ['玉门关（初步筛选）', '玉门关（文学版）', '阳关（初步筛选）', '阳关（文学版）']
    for i in range(sheet_num):
        text = pd.read_excel('dataset.xlsx', engine="openpyxl", header=None, sheet_name=i)
        list_text = text.loc[:,0].tolist()
        results = senta.sentiment_classify(data={"text": list_text})
        column_name = results[0].keys()
        df = pd.DataFrame(columns=column_name)
        count = 0
        for result in results:    
            for key, value in result.items():
                df.loc[count, key] = value
            count += 1 
        df.to_excel('{}.xlsx'.format(sheet_name[i]))
    """

    text = pd.read_excel('dataset.xlsx', engine="openpyxl", header=None, sheet_name=1)
    list_text = text.loc[:,0].tolist()
    results = senta.sentiment_classify(data={"text": list_text})
    column_name = results[0].keys()
    df = pd.DataFrame(columns=column_name)
    count = 0
    for result in results:    
        for key, value in result.items():
            df.loc[count, key] = value
        count += 1 
    df.to_excel('玉门关（文学版）.xlsx')

if __name__ == "__main__":
    main()
