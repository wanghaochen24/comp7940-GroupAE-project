FROM python
WORKDIR /chatbot
COPY . /chatbot
RUN pip install update
RUN pip install -r requirements.txt

ENV TLG_ACCESS_TOKEN=6972742316:AAGfE5-aYPEoQN4SF1J5mgaqgm5oi9AQl0Q
ENV BASICURL=https://chatgpt.hkbu.edu.hk/general/rest
ENV MODELNAME=gpt-4-turbo
ENV APIVERSION=2023-12-01-preview
ENV ACCESS_TOKEN=9161384b-ce21-41cc-b0bd-d2fdc5258ee7
ENV USER=shun
ENV PASSWORD=Qwer1234
ENV HOST=shun.mysql.database.azure.com

CMD python GroupAE_chatbot.py