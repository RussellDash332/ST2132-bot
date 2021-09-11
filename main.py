import requests, textract, datetime, re, emoji
from env import TOKEN, ST2132

def main(curr_id):
    curr = datetime.datetime.now() - datetime.timedelta(days=1)
    msg = ""

    while True:
        curr += datetime.timedelta(days=1)
        temp = curr.strftime("%d %b %Y").split(" ")
        
        lecture_date = f'{int(temp[0])}_{temp[1][:3]}_{temp[2]}'
        
        try:
            lecture_link = re.findall(r"\bhttps://nus-sg\.zoom\.us[^ ]*", textract.process(f"Zoom meeting_{lecture_date}.docx").decode("utf-8").replace("\n"," "))[0]
            day = curr.strftime('[%d %b] %A')

            # Accept typos one day before or after
            if day in ["Thursday", "Saturday"]:
                day = "Friday"
            elif day in ["Monday", "Wednesday"]:
                day = "Tuesday"

            msg += f"*{day}'s Lecture*\n{lecture_link}"

            # Tutorials can be traced from the day before
            tutorials = {1: "12-1", 2: "1-2", 3: "2-3", 4: "3-4", 5: "4-5"}
            tut = curr - datetime.timedelta(days=1)

            # Check for the next one week
            while (tut-curr).days <= 7:
                tut_temp = tut.strftime("%d %b %Y").split(" ")
                tut_day = tut.strftime("[%d %b]")
                tut_date = f'{int(tut_temp[0])}_{tut_temp[1][:3]}_{tut_temp[2]}'

                for i in range(1,6):
                    try:
                        tut_link = list(filter(lambda x: "pwd" in x, re.findall(r"\bhttps://nus-sg\.zoom\.us[^ ]*", textract.process(f"Zoom meeting_tutorial_{tutorials[i]}_pm_{tut_date}.docx").decode("utf-8").replace("\n"," "))))[0]
                        msg += f"\n\n*{tut_day} Tutorial (Group {i}, {tutorials[i]}PM)*\n{tut_link}"
                    except:
                        pass
                tut += datetime.timedelta(days=1)

            # Double checking
            print(msg)
            input("\nAll done!\nPress enter to confirm and quit...")

            # Voila!
            print(send(msg, ST2132)) # take note of the next curr_id
            delete(ST2132, curr_id)
            return
        except:
            # Lectures are at most before 2021, so exit the loop
            if curr.year > 2021:
                break

    input("Rip, no lecture link no fun.")

# Some unoptimized code but does the job on sending messages manually
def send(bot_message, chat_id):
    bot_token = TOKEN
    send_text = emoji.emojize('https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message + '&disable_web_page_preview=true', use_aliases = True)

    response = requests.get(send_text)

    return response.json()

def delete(chat_id, msg_id):
    response = requests.get(f'https://api.telegram.org/bot{TOKEN}/deleteMessage?chat_id={chat_id}&message_id={msg_id}')
    # return response.json()

# Manual assignment if needs to delete previous messages
curr_id = "???"
main(curr_id)
