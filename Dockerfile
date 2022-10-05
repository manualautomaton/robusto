FROM python:3.10.0

RUN pip install flask requests actionpack
ADD robusto/ /robusto
WORKDIR /robusto
ENV FLASK_APP=/robusto
CMD ["flask", "--app", "server.py", "run", "--host=0.0.0.0"]