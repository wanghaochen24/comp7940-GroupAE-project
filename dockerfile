FROM python
WORKDIR /APP
COPY . /APP
RUN pip install update
RUN pip install -r requirements.txt

ENV TLG_ACCESS_TOKEN=6972742316:AAGfE5-aYPEoQN4SF1J5mgaqgm5oi9AQl0Q
ENV BASICURL=https://chatgpt.hkbuedu.hk/general/rest
ENV MODELNAME=gpt-4-turbo
ENV APIVERSION=2023-12-01-preview
ENV ACCESS_TOKEN=5bab5ac0-850c-4ee6-9ae7-566742cc000a
CMD python chatbot.py