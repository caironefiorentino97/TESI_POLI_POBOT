# THESIS_CAIRONE_FIORENTINO
Politecnico of Turin Thesis: "Implementation and Evaluation of an Educational Chatbot based on NLP Techniques"

# GENERATE TOKEN SLACK
NB: REMEMBER TO REGENERATE SLACK TOKENS AND CHANNEL ID IF ARE DISABLE (SEE THESIS PDF)
- Go on your Slack App in api.slack.com/apps -> select your app or create new -> Settings -> Install App -> (regenerate two tokens) -> Copy Tokens in `actions/Constants.py` file

# RASA - LOCAL MODE
## Components Installation

- Writing in Anaconda console this command:
  - `conda create --name venv python==3.8.0`
  - `conda activate venv`
  - `conda install ujson tensorflow`
  - `pip install rasa` 
  - `pip install rasa[spacy]` for SPACY configuration
  - `pip install rasa[trasformers]` for BERT configuration  
  - `rasa init` if you want to create new project
  
MORE INFO: See this video: [link](https://www.youtube.com/watch?v=4ewIABo0OkU&list=PL75e0qA87dlEWUA5ToqLLR026wIkk2evk&index=1)

## Code Execution
- First, in `TESI_NLP` directory do the training in anaconda console with `venv` activate:
  - `rasa train --config configs/{file_cofiguration}.yml --fixed-model-name {model_name}`

- After run server rasa:
 - `rasa run --connector slack --model {model_name} --debug`
   
- In an other prompr run server rasa ACTIONS:
 - `rasa run actions --action actions --debug`
   
- If you want,to test locally the intent classification, run in Anaconda console:
  - `rasa train --config configs/{file_cofiguration}.yml --fixed-model-name {model_name}`
  - `rasa shell --model {model_name}`
  
    
## Rasa Bot - Slack Connection
- after  training and running the server in Anaconda console (see `## Execution of code` paragraph): 
  - in `BOT_RASA/ngrok` directory run this command (in console prompt):
    - `ngrok http 5005` to create a tunnel for `localhost:5005` address:
    - select the forwarding address choose to ngrok ({address} = http://<number_code>.ngrok.io)
    - in Slack App [link](https://api.slack.com/apps/A020AHLC396/app-home) save the address (selecting in `Features` menu):
      - Interactivity & Shortcut > Request URL: ({address}/webhooks/slack/webhook) > Save Changes
      - OAuth & Permissions > Redirect URLs > Add : ({address}/webhooks/slack/webhook) > Save URLs
      - Event Subscriptions > Enable Events (Request URL) > Change: ({address}/webhooks/slack/webhook) > Save Changes
    - expired time of ngrok address: 2 hours. (when we will use a public address, ngrok will become USELESS)  
- tokens bot save as environment variable in PC server (for security issue)
- Slack bot: [link](https://app.slack.com/client/T01UMQBQAE5/D01V10KMHJ7)

To Connect also the ACTION Server Rasa:
- `ngrok http 5055` to create a tunnel for `localhost:5055`
- In `endpoints.yml` modify `url` of `action_endpoint`: `{address}/webhook`

# RASA X
## Components Installation

- Writing in Anaconda console this command:
  - `conda create --name venv python==3.9.0`
  - `conda activate venv`
  - `conda install ujson tensorflow`
  - `pip install rasa[spacy]` for SPACY configuration
  - `pip install rasa[trasformers]` for BERT configuration  
  - `pip install --upgrade pip==20.0.1`
    `pip3 install rasa-x --extra-index-url https://pypi.rasa.com/simple`
    `pip install --upgrade pip`

## Code Execution
- First, in `TESI_NLP` directory do the training in anaconda console with `venv` activate:
  - `set PYTHONUTF8=1`
  - `rasa x --connector slack --config configs/{file_cofiguration}.yml`
   
- In an other prompt run server rasa ACTIONS:
 - `rasa run actions --action actions --debug`
    
## Rasa Bot - Slack Connection
- after  training and running the server in Anaconda console (see `## Execution of code` paragraph): 
  - in `BOT_RASA/ngrok` directory run this command (in console prompt):
    - `ngrok http 5005` to create a tunnel for `localhost:5005` address:
    - select the forwarding address choose to ngrok ({address} = http://<number_code>.ngrok.io)
    - in Slack App [link](https://api.slack.com/apps/A020AHLC396/app-home) save the address (selecting in `Features` menu):
      - Interactivity & Shortcut > Request URL: ({address}/webhooks/slack/webhook) > Save Changes
      - OAuth & Permissions > Redirect URLs > Add : ({address}/webhooks/slack/webhook) > Save URLs
      - Event Subscriptions > Enable Events (Request URL) > Change: ({address}/webhooks/slack/webhook) > Save Changes
    - expired time of ngrok address: 2 hours. (when we will use a public address, ngrok will become USELESS)  
- tokens bot save as environment variable in PC server (for security issue)
- Slack bot: [link](https://app.slack.com/client/T01UMQBQAE5/D01V10KMHJ7)

To Connect also the ACTION Server Rasa:
- `ngrok http 5055` to create a tunnel for `localhost:5055`
- In `endpoints.yml` modify `url` of `action_endpoint`: `{address}/webhook`

To Connect also the ACTION Server Rasa X:
- `ngrok http 5055` to create a tunnel for `localhost:5002`
- In `credentials.yml` modify `url` of `rasa`: `{address}/api`


# RASA - DOCKER MODE
## Code Execution
If is the first time, run this commands:
``` 
docker volume create db-volume
docker-compose up -d
docker-compose down
docker-compose up -d
python rasa_x_commands.py create --update admin me <password_rasa_server> (i.e. password)
docker-compose down
docker-compose up -d
```

Otherwise, in `TESI_NLP` directory in console run only this command:
- `docker-compose up -d`

## Rasa Bot - Slack Connection

After all container is in running mode, in web browser go in `http:://localhost:80' and insert the password choose the first time. (i.e. password)

If rasa x server not contain NLU data (possible first time) you can upload the file directly using interface of rasa x server in `Training -> NLU data / Stories / Rules / Configuration (copy and paste the content of config choose in TESI_NLP directory)`  

If you want to connect to slack:
- after  training and running the server in Anaconda console (see `## Execution of code` paragraph): 
  - in `BOT_RASA/ngrok` directory run this command (in console prompt):
    - `ngrok http 80` to create a tunnel for `localhost:80` address:
    - select the forwarding address choose to ngrok ({address} = http://<number_code>.ngrok.io)
    - in Slack App [link](https://api.slack.com/apps/A020AHLC396/app-home) save the address (selecting in `Features` menu):
      - Interactivity & Shortcut > Request URL: ({address}/core/webhooks/slack/webhook) > Save Changes
      - OAuth & Permissions > Redirect URLs > Add : ({address}/core/webhooks/slack/webhook) > Save URLs
      - Event Subscriptions > Enable Events (Request URL) > Change: ({address}/core/webhooks/slack/webhook) > Save Changes
    - expired time of ngrok address: 2 hours. (when we will use a public address, ngrok will become USELESS)  
- tokens bot save as environment variable in PC server (for security issue)
- Slack bot: [link](https://app.slack.com/client/T01UMQBQAE5/D01V10KMHJ7)

# RASA - TEST DATA
## Test stories in tests directory
- if you want tests stories with cross-validation:
  - `rasa train --config configs/{file_cofiguration}.yml --fixed-model-name {model_name}` (if model does not exist)
  - `rasa test --config configs/{file_cofiguration}.yml  --cross-validation --runs {time_runs} --folds {num_folds}  --out {dir_out} --model {model_name}`

## Test NLU data
- if you want test only the NLU data splitted:
  - `rasa train nlu --nlu train_test_split/training_data.yml --config configs/{file_cofiguration}.yml --fixed-model-name ./models_NLU/{model_name}` (if model does not exist)
  - `rasa test  nlu --nlu train_test_split/test_data.yml  --out {dir_out} --model ./models_NLU/{model_name}`
  
- if you want test only the NLU data totally:
  - `rasa train nlu --config configs/{file_cofiguration}.yml --fixed-model-name {model_name}` (if model does not exist)
  - `rasa test  nlu --nlu train_test_split/test_data.yml --out {dir_out} --model {model_name}`
  
## Test CORE data
- if you want test only the CORE data:
  - `rasa train --config configs/{file_cofiguration}.yml --fixed-model-name {model_name}` (if model does not exist)
  - `rasa test  core --stories tests/test_stories.yml --out {dir_out} --model {model_name}`

