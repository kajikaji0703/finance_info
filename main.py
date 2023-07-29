# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 14:18:49 2023

@author: r00466125
"""

import streamlit as st # フロントエンドを扱うstreamlitの機能をインポート
import pandas as pd # データフレームを扱う機能をインポート
import yfinance as yf # yahoo financeから株価情報を取得するための機能をインポート
#import altair as alt # チャート可視化機能をインポート
import openai # openAIのchatGPTのAIを活用するための機能をインポート

# アクセスの為のキーをopenai.api_keyに代入し、設定
openai.api_key = "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"

# @st.cache_dataで読み込みが早くなるように処理を保持しておける
@st.cache_data
#ｇｐｔに　変数込みのプロンプトを入力し、　出力を返す関数
def run_gpt(company,info_mode, data ,term):
    # リクエスト内容を決める  
    #st.write(term)
    if  info_mode=="財務諸表" or info_mode =="B/S:バランスシート"or info_mode == "キャッシュフロー":
        request_to_gpt =  company +"の"+ info_mode +"の以下の" +term + "分のデータを分析して　分かることを教えて下さい \n"+ data
    elif  info_mode == "株価":
        request_to_gpt =  company +"の"+ info_mode +"の以下の" +term +"日分のデータ を分析して　分かることを教えて下さい \n"+ data
    else:
        request_to_gpt = data[0] + data[1] + " リンクの内容を日本語で要約してください。内容は文字500文字以内で出力してください。"
    
    # 決めた内容を元にopenai.ChatCompletion.createでchatGPTにリクエスト。オプションとしてmodelにAIモデル、messagesに内容を指定
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": request_to_gpt },
        ],
    )

    # 返って来たレスポンスの内容はresponse.choices[0]["message"]["content"].strip()に格納されているので、これをoutput_contentに代入
    output_content = response.choices[0]["message"]["content"].strip()
    return output_content # 返って来たレスポンスの内容を返す


st.title("金融情報分析アプリ") # タイトル
# 取得したデータから抽出するための配列を生成し、companiesに代入

company_list = pd.read_excel("data_j_edit.xlsx")
company_list = company_list[company_list["規模コード"].isin([1,2,4])]

type_list = list(company_list["17業種区分"].unique())

company_type = st.selectbox(
    '業種を選択してください。',
    type_list)

company_list = company_list[company_list["17業種区分"]== company_type]
company_list = company_list.set_index('銘柄名')['コード']
company_list = company_list.astype(str) + ".T"

company = st.selectbox(
    '会社名を選択してください。',
    company_list.index
)

#どの金融情報を表示するか選択
mode = ["株価","財務諸表","B/S:バランスシート","キャッシュフロー","ニュース"]
info_mode = st.selectbox("表示情報の種類",options=mode)

#st.write(company_list[company]) 
df_c= yf.Ticker(company_list[company])


if info_mode == "株価":
    st.write("こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。") # サイドバーに表示  
    st.write("表示日数選択") # サイドバーに表示 
    days = st.slider('日数', 1, 50, 20) # サイドバーに表示　取得するための日数をスライドバーで表示し、daysに代入
    st.write(f"過去 {days}日間 の株価") # 取得する日数を表示
    
    # チャートに表示する範囲をスライドで表示し、それぞれをymin, ymaxに代入
    #st.write("株価の範囲指定") # サイドバーに表示

    df_t = df_c.history(period=f'{days}d')
    df_t.index = df_t.index.strftime('%d %B %Y') # indexを日付のフォーマットに変更
    df_t = df_t[['Close']] # データを終値だけ抽出
    df_t.columns = [company] # データのカラムをyf.Tickerのリクエストした企業名に設定
    
    df_t = df_t.T # 欲しい情報が逆なので、転置する
    df_t.index.name = 'Name' # indexの名前をNameにする
    st.write("株価 ", df_t) # dataにあるindexを表示
    
elif info_mode == "財務諸表":
    tmp = df_c.financials
    tmp.columns = tmp.columns.strftime('%d %B %Y')
    st.dataframe(tmp)
    df_t = df_c.financials
    df_t.index.name = "financials"
    
elif info_mode == "B/S:バランスシート":
    tmp = df_c.balance_sheet
    tmp.columns = tmp.columns.strftime('%d %B %Y')
    st.dataframe(tmp)
    df_t = df_c.balance_sheet
    df_t.index.name = "balance_sheet"
elif info_mode == "キャッシュフロー":
    tmp = df_c.cashflow
    tmp.columns = tmp.columns.strftime('%d %B %Y')
    st.dataframe(tmp)
    df_t = df_c.cashflow
    df_t.index.name = "cash_flows"
elif  info_mode == "ニュース":
    news = df_c.news
    titles = [news[i]["title"] for i in range(len(news))]
    news_title = st.selectbox(company+"に関するニュース",options=titles)
    if st.button(news_title+"を要約する"):
        index_of_value = titles.index(news_title)
        df_data= [news[index_of_value]["title"],news[index_of_value]["link"]]
        output_content_text = run_gpt(company,info_mode, df_data,0)
        st.write(output_content_text)
    
if  info_mode != "ニュース":
    if info_mode != "株価":
        df_data = df_t.to_csv()
    elif info_mode == "株価":
        df_data = df_t.to_csv(index=False)
        
    if st.button(info_mode+"の分析を実施する"):
        if info_mode != "株価":
            output_content_text = run_gpt(company,info_mode, df_data, "4年")
        elif info_mode == "株価":
            days = str(days)
            output_content_text = run_gpt(company,info_mode, df_data, days)

        # 代入された文字を表示
        st.write(output_content_text)