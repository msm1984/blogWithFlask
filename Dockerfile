FROM python:alpine
LABEL author="MOHAMAD SADEGH MONTAZERI <sadeghmomo2020@gmail.com>"
WORKDIR /app
COPY templates/requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install wheel
RUN pip install flask gunicorn
COPY wsgi.py /app/
COPY templates/*.html /app/templates/
COPY templates/inc/*.html /app/templates/inc/
COPY instance/mydb.db /app/instance/
COPY app.py /app/
EXPOSE 5000
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app