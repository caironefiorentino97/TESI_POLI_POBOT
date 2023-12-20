import threading
from rasa.core.channels.slack import SlackBot
from rasa_sdk.events import ConversationPaused, ConversationResumed
from rasa_sdk import Action
from typing import Text
from actions import Costants
import sqlite3
from slack import WebClient
import json
import asyncio
from rasa_sdk.events import SlotSet
import time

# send request text-buttons and manage DB ------------------------------------------ #
async def send_request_db_and_buttons(tracker, question):
    conn = sqlite3.connect('./actions/db/richieste.db')
    slack_conn = SlackGeneral()
    user_info = slack_conn.slack_items(tracker.sender_id)
    id_student = user_info['user']['id']
    name_student = user_info['user']['name']
    thread_vect = tracker.latest_message['metadata']['thread_id'].split(".")
    thread_id = thread_vect[0] + thread_vect[1]
    cursor = conn.execute("INSERT INTO Richiesta(IdStud,Domanda,ThreadId) VALUES(?,?, ?)",
                          [id_student, question, thread_id])
    id_req = cursor.lastrowid
    conn.commit()
    cursor = conn.execute("SELECT IdProf FROM Docente")
    id_profs = []
    for row in cursor:
        id_profs.append(row[0])
        conn.execute("INSERT INTO Richiesta_Docente(IdRiq, IdProf, Disponibile) VALUES(?,?,?)",
                     [id_req, row[0], 1])
    conn.commit()
    conn.execute("UPDATE Richiesta_Docente SET Disponibile=0 WHERE  IdRiq=? AND IdProf=?",
                 [id_req, id_profs[0]])
    conn.commit()
    conn.close()
    await send_text_buttons(name_student, question, thread_id, id_req, id_profs[0], len(id_profs))


# prof send request to an other prof
async def resend_request_db_and_buttons(tracker):
    accepted = tracker.latest_message['entities'][0]['value']
    id_riq = tracker.latest_message['entities'][1]['value']
    prof_id_req = tracker.latest_message['entities'][2]['value']
    conn = sqlite3.connect('./actions/db/richieste.db')
    # get info student and question
    cursor = conn.execute("SELECT IdStud, Domanda, ThreadId  FROM Richiesta WHERE idRiq=?", [id_riq])
    row = cursor.fetchone()
    stud_id = row[0]
    question = row[1]
    thread_id = row[2]
    if accepted == 'True':
        slack_client = SlackBot(token=Costants.SLACK_BOT_TOKEN, slack_channel=Costants.CHANNEL_ID)
        text_res = "<@{0}> : il professore <@{1}> ha preso in carico la tua domanda. Attendi il suo arrivo su questo " \
                   "canale.".format(stud_id, prof_id_req)
        await slack_client.send_text_message(recipient_id=Costants.CHANNEL_ID, text=text_res)
    else:
        slack_conn = SlackGeneral()
        user_info = slack_conn.slack_items(stud_id)
        name_stud = user_info['user']['name']
        # select all free profs
        cursor = conn.execute("SELECT idProf FROM Richiesta_Docente WHERE idRiq=? AND Disponibile=1", [id_riq])
        free_profs = []
        for row in cursor:
            free_profs.append(row[0])
        # choose the next prof to send request
        conn.execute("UPDATE Richiesta_Docente SET Disponibile=0 WHERE  IdRiq=? AND IdProf=?",
                     [id_riq, free_profs[0]])
        conn.commit()
        await send_text_buttons(name_stud, question, thread_id, id_riq, free_profs[0], len(free_profs))
    conn.close()


async def send_text_buttons(question, thread_id, id_req, id_prof, num_prof_free):
    link = "{0}/archives/{1}/p{2}".format(Costants.SLACK_URL, Costants.CHANNEL_ID, thread_id)
    REQUEST = "/answer"
    if num_prof_free > 1:
        buttons = [
            {
                "title": "Accetta",
                "payload": REQUEST + json.dumps({"accepted": 'True', "idRiq": str(id_req), "idProf": str(id_prof)})
            },
            {
                "title": "Passa ad un altro docente",
                "payload": REQUEST + json.dumps({"accepted": 'False', "idRiq": str(id_req), "idProf": str(id_prof)})
            }
        ]
    elif num_prof_free <= 1:
        buttons = [
            {
                "title": "Accetta Richiesta",
                "payload": REQUEST + json.dumps({"accepted": 'True', "idRiq": str(id_req), "idProf": str(id_prof)})
            }
        ]
    slack_general = SlackGeneral()
    channel_direct_conv_id = slack_general.create_direct_conversation(id_prof)
    slack_client = SlackBot(token=Costants.SLACK_BOT_TOKEN, slack_channel=channel_direct_conv_id)
    await slack_client.send_text_message(recipient_id=channel_direct_conv_id, text=link)
    await slack_client.send_text_with_buttons(recipient_id=channel_direct_conv_id, text="Accetti la richiesta?",
                                              buttons=buttons)


# asyncio call method threads ------------------------------------------ #
def async_request_db_buttons(tracker, question):
    event_loop_a = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop_a)
    event_loop_a.run_until_complete(send_request_db_and_buttons(tracker, question))


def async_resend_request_db_buttons(tracker):
    event_loop_b = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop_b)
    event_loop_b.run_until_complete(resend_request_db_and_buttons(tracker))


# general class to manage slack request ------------------------------------------ #
class SlackGeneral(WebClient):
    def __init__(self):
        self.slack = WebClient(Costants.SLACK_BOT_TOKEN)
        self.channel_direct_conversation = None

    def slack_items(self, username):
        userinfo = self.slack.users_info(user=username)
        return userinfo

    def create_direct_conversation(self, user1):
        response = self.slack.conversations_open(users=[user1])
        self.channel_direct_conversation = response['channel']['id']
        return self.channel_direct_conversation

    def send_message(self, channel, text):
        self.slack.chat_postMessage(channel=channel, text=text)


# action to send request at prof ------------------------------------------ #
class ActionSendRequestHelp(Action):

    def __init__(self):
        self.last_text = None
        self.last_user = None
        self.time = time.time()

    def name(self) -> Text:
        return 'action_send_help'

    def run(self, dispatcher, tracker, domain):
        ConversationPaused()
        question = tracker.get_slot("question")
        user = tracker.latest_message['metadata']['users'][0]
        text = tracker.latest_message['text']
        now = time.time()
        # send message if text and user is not same or if is passed 1 minutes after last equals messages
        # of same user (to not have multiple messages problems)
        if text != self.last_text or self.last_user != user or (now - self.time) >= 60:
            thread = threading.Thread(target=async_request_db_buttons, args=(tracker, question))
            dispatcher.utter_message(text="Richiesta inviata!")
            self.last_text = text
            self.last_user = user
            self.time = now
            thread.start()
        else:
            dispatcher.utter_message(text="Attendi almeno un minuto per ripostare la domanda ...")
        return [SlotSet("question", None), ConversationResumed()]


# action to answer question of student ------------------------------------------ #
class ActionAnswer(Action):
    def name(self) -> Text:
        return 'action_answer'

    def run(self, dispatcher, tracker, domain):
        thread = threading.Thread(target=async_resend_request_db_buttons, args=(tracker,))
        thread.start()
        dispatcher.utter_message(text="OK")
        return []
