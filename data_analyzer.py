import streamlit as st
import groq
import pandas as pd
import plotly.express as px
import json
import re
import os

client = groq.Groq(api_key=os.environ.get('GROQ_API_KEY'))

st.title('Data Analyzer Agent')
st.write('Koi bhi Excel ya CSV upload karo - AI analyze karega!')

uploaded_file = st.file_uploader('File choose karo', type=['xlsx', 'csv'])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader('Raw Data')
    st.dataframe(df)

    st.subheader('Basic Stats')
    st.write(df.describe())

    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    if numeric_cols:
        st.subheader('Charts')

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(df, x=df.columns[0], y=numeric_cols[0], title='Bar Chart')
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(df, x=df.columns[0], y=numeric_cols[0], title='Line Chart')
            st.plotly_chart(fig2, use_container_width=True)

        if len(numeric_cols) >= 2:
            col3, col4 = st.columns(2)
            with col3:
                fig3 = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title='Scatter Plot')
                st.plotly_chart(fig3, use_container_width=True)
            with col4:
                fig4 = px.histogram(df, x=numeric_cols[0], title='Distribution')
                st.plotly_chart(fig4, use_container_width=True)

    with st.spinner('AI analysis kar raha hai...'):
        try:
            sample = df.head(20).to_string()
            stats = df.describe().to_string()

            response = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[
                    {'role': 'system', 'content': 'You are a data analyst. Analyze the data and return ONLY a JSON object with: {"summary": "overall summary", "key_insights": ["insight 1", "insight 2", "insight 3"], "trends": "trends observed", "recommendations": ["rec 1", "rec 2"]}. Return ONLY JSON.'},
                    {'role': 'user', 'content': 'Analyze this data and give insights in plain text numbers only (no latex or math formatting): ' + sample + ' Stats: ' + stats}
                ]
            )

            raw = response.choices[0].message.content
            json_match = re.search(r'{.*}', raw, re.DOTALL)

            if json_match:
                analysis = json.loads(json_match.group())

                st.subheader('AI Summary')
                st.info(analysis.get('summary', 'N/A'))

                st.subheader('Key Insights')
                for insight in analysis.get('key_insights', []):
                    st.success('- ' + str(insight))

                st.subheader('Trends')
                st.warning(analysis.get('trends', 'N/A'))

                st.subheader('Recommendations')
                for rec in analysis.get('recommendations', []):
                    st.info('- ' + str(rec))

        except groq.AuthenticationError:
            st.error('API Key galat hai!')
        except groq.RateLimitError:
            st.error('Thodi der baad try karo!')
        except Exception as e:
            st.error('Kuch galat hua - dobara try karo!')
