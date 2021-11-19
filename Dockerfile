FROM rasa/rasa:2.7.0-full
# Use subdirectory as working directory
WORKDIR /app

# Copy any additional custom requirements, if necessary (uncomment next line)
# Change back to root user to install dependencies
USER root

# Install extra requirements for actions code, if necessary (uncomment next line)
RUN pip install rasa-sdk==2.6.0
RUN pip install bert
RUN pip install spacy
RUN pip install transformers
RUN pip install rasa[spacy]
RUN pip install rasa[trasformers]
RUN python -m spacy download it_core_news_md

RUN chmod 774 -R /app

# Copy folders to working directory
COPY ./.config /.config
COPY ./db /app/db
COPY ./models /app/models
COPY ./data /app/data
COPY ./*.yml /app
COPY ./*.py /app
COPY ./.env /app
COPY ./events.db /app
COPY ./events.db-shm /app
COPY ./events.db-wal /app
COPY ./rasa /app
COPY ./rasa.db /app
COPY ./cache_bert /app/cache_bert

RUN chmod 774 -R /app
USER 1001