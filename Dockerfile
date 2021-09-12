FROM python:3.9
WORKDIR /src
COPY . .
# RUN mkdir /src
# COPY src ./src
# WORKDIR /src
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]