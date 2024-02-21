FROM python:3.11

RUN pip install virtualenv
ENV VIRTUAL_ENV=/venv
RUN virtualenv venv -p python3
ENV PATH="VIRTUAL_ENV/bin:$PATH"

WORKDIR /App_LLM_StructuredData

#RUN git clone https://github.com/sunyan-SG/Streamlit-PandasAI.git .
COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8501

#HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

#ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501"]
CMD streamlit run app.py