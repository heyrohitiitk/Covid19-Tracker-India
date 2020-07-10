import smtplib
import ssl
import credentials as cd
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import json
from datetime import datetime
import pytz


def setLog(msg=None, satis=-1):
    FORMAT = "[%(asctime)-15s]: %(levelname)s :%(message)s"
    logging.basicConfig(
        level=logging.DEBUG, filename="test.log", format=FORMAT,
    )
    if satis == 1:
        logging.debug(msg)
    else:
        logging.error(msg)


smtp_server = "smtp.gmail.com"
port = 587
sender_email = cd.email
receiver_email = cd.email
password = cd.password
message = MIMEMultipart("alternative")
message["Subject"] = "Corona Tracker"
message["From"] = sender_email
message["To"] = receiver_email  # cd.receiver1


def sendError(obj, msg):
    part = MIMEText(msg, "plain")
    message.attach(part)

    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_server, port)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())


def load():
    check = os.path.getsize("past_data.json")
    if check == 0:
        return None

    with open("past_data.json", "r") as f:
        res = json.load(f)
    return res


def save(x):
    with open("past_data.json", "w") as f:
        json.dump(x, f, indent=2)


def changeForState(json_stat, site_stat, state):
    for x in json_stat:
        if x[1].lower() == state.lower():
            from_json = x
            break
    for x in site_stat:
        if x[1].lower() == state.lower():
            from_site = x
            break
    new_stat = []
    for i in range(2, len(from_json)):
        new_stat.append(int(from_site[i]) - int(from_json[i]))
    return new_stat


def sendMail(obj, state=""):
    data = obj.data_set.iloc[:-1]
    if state.lower() not in list(data.get("States")):
        state = "Delhi"

    cur_time = datetime.now(tz=pytz.timezone("Asia/Kolkata")).date()
    saver_data = {
        "update_time": str(cur_time),
        "quick_list": obj.quick_list,
        "stat": obj.stat,
    }
    get_json_data = load()
    change = 0
    if get_json_data == None:
        change = 0
        save(saver_data)
    else:
        from_json = get_json_data.get("quick_list")
        from_site = obj.quick_list
        overall = [
            from_site.get("Active Cases") - from_json.get("Active Cases"),
            from_site.get("Cured / Discharged") - from_json.get("Cured / Discharged"),
            from_site.get("Deaths") - from_json.get("Deaths"),
            from_site.get("Migrated") - from_json.get("Migrated"),
        ]

        state_changes = changeForState(get_json_data.get("stat"), obj.stat, state)
        if any(overall):
            change = 1

        json_time = get_json_data.get("update_time")
        if str(cur_time) != json_time:
            save(saver_data)

    if change == 0:
        overall = [0, 0, 0, 0]
        state_changes = [0, 0, 0, 0]

    li = data[data["States"] == state.lower()]
    mp = {
        "state": li.iloc[0, 1],
        "active": li.iloc[0, 2],
        "death": li.iloc[0, 4],
        "recovered": li.iloc[0, 3],
        "confirmed": li.iloc[0, 5],
    }
    time = obj.at_time
    tests = obj.test_done
    qemail = obj.query_email
    data_list = obj.quick_list
    total = sum([int(x) for x in data_list.values()])
    try:
        text = f"""\
            CORONAVIRUS CURRENT STATUS (INDIA)
            Data as on : {time}
            Total Confirmed :{total}
            ACTIVE CASES :{data_list['Active Cases']}
            Cured/Discharded : {data_list['Cured / Discharged']}
            DEATHS : {data_list['Deaths']}
            MIGRATED : {data_list['Migrated']}
            
            {mp['state'].upper()} STATUS
            Total Confirmed : {mp['confirmed']}
            ACTIVE CASES :{mp['active']}
            Cured/Discharded : {mp['recovered']}
            DEATHS : {mp['death']}
            
            ------------------------------------------------------------
            {tests}
            For any Technical query email at :{qemail}
            
            For More Information Visit at: 'https://www.mohfw.gov.in/'
            """

        html = f"""\
            <html>
            <body>
                <h1>CORONAVIRUS CURRENT STATUS (INDIA)</h1>
                <h3>Data as on : {time}</h3>
                <p><b>Total Confirmed :</b>{total}</p>
                <p><b>ACTIVE CASES</b> :{data_list['Active Cases']} (+{overall[0]})</p>   
                <p><b>Cured/Discharded</b> : {data_list['Cured / Discharged']} (+{overall[1]})</p>
                <p><b>DEATHS </b>: {data_list['Deaths']} (+{overall[2]})</p>
                <p><b>MIGRATED</b> : {data_list['Migrated']} (+{overall[3]})</p>
                <br>
                <h2>{mp['state'].upper()} STATUS</h2>
                <p><b>ACTIVE CASES</b> :{mp['active']} (+{state_changes[0]})</p>   
                <p><b>Cured/Discharded</b> : {mp['recovered']} (+{state_changes[1]})</p>
                <p><b>DEATHS </b>: {mp['death']} (+{state_changes[2]})</p>
                <p><b>Total Confirmed :</b>{mp['confirmed']} (+{state_changes[3]})</p>                
                <p>--------------------------------------------------</p>
                <p>{tests}</p>
                <p>For any Technical query email at :{qemail}</p>
                <br>
                <p>For More Information Visit at: <a href='https://www.mohfw.gov.in/'>mohfw.gov.in</a></p>
            </body>
            </html>
            """
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        # -------------------------
        filename = "covid_donut_graph.png"
        with open(filename, "rb") as attachment:
            party = MIMEBase("application", "octet-stream")
            party.set_payload(attachment.read())
        encoders.encode_base64(party)
        party.add_header(
            "Content-Disposition", f"attachment; filename= {filename}",
        )
        message.attach(party)
        # -------------------------

        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        setLog(f"Stats send successfuly to {receiver_email}", 1)
    except Exception as e:
        msg = f"Exception Occured in gmail.py->sendMail(): {e.__class__.__name__} : {e}"
        setLog(msg)
        sendError(obj, msg)
    finally:
        server.quit()
