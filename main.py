
from typing import Final
from telegram import Update
import psycopg2
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import datetime
from twilio.rest import Client

date_format = "%Y-%m-%d"

TOKEN: Final = "5966745825:AAGgph6Ms6-Jd_YNEfHJ5eKy2fMOTm5iIJU"
access_keys_list: Final = ["dfkdfkdh324", "fhjdhfjhs73t82", "dfhdifhh78234", "DR.RICHA@#67", "DEVRAJSIR#@1"]

# SQL database connection
# global cursor
connection = psycopg2.connect(
    host="localhost",
    port=5432,
    database="MedicineMangement",
    user="postgres",
    password="Qwert@123",
)

# Create a cursor object
cursor = connection.cursor()

#

post_user = 0


# /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Medicine Management Services. Made with ❤ by @luvvrisshii."
    )
    await update.message.reply_text(
        "If you are a new user, Kindly Proceed with the /profile command"
    )
    await update.message.reply_text(
        "If you are already the part of the family, Kindly Proceed with the other commands"
    )
    await update.message.reply_text(
        "For any Query, Please contact admin @luvvrisshii or Use the /help command"
    )
    return ConversationHandler.END


async def user_profile_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide the access key")
    return "access_key"


async def access_key_validation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    access_key = update.message.text
    if access_key in access_keys_list:
        await update.message.reply_text("Access key accepted")
        context.user_data["access_key"] = access_key
        await update.message.reply_text("What's your name?")
        return "name"
    else:
        await update.message.reply_text("Invalid access key")
        return ConversationHandler.END


async def name_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data["name"] = name
    await update.message.reply_text("What's your age?")
    return "age"


async def age_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = update.message.text
    context.user_data["age"] = age
    await update.message.reply_text("What's your gender?")
    return "gender"


async def gender_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text
    context.user_data["gender"] = gender

    await update.message.reply_text("Thank you for providing your information.")
    await update.message.reply_text("Allow us a couple of seconds to register you")

    # return "user_id_generate"  # Update the return value to transition to "user_id_generate" state
    return await user_id_generate(update, context)


# Code for user_id generation


async def user_id_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # post_user = context.user_data.get("post_user", 0) + 1
    # context.user_data["post_user"] = post_user
    global post_user
    post_user = post_user + 1
    user_id = f"LRMEDUSR{post_user}"
    context.user_data["user_id"] = user_id
    await usr_access_map(update, context)

    await update.message.reply_text("You are Successfully Registered.")
    await update.message.reply_text(
        "You may go ahead in setting up the medicine remainders"
    )
    await update.message.reply_text("If faced any issue, kindly use the /help command")

    return ConversationHandler.END


# Mapping the user and accesskey

async def usr_access_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sql = """
    INSERT INTO user_id_access_key_map (access_key, user_id)
    VALUES (%s, %s)
    """

    # Fethcing the required
    user_id = context.user_data["user_id"]
    access_key = context.user_data["access_key"]

    # Bind the values to the SQL statement
    values = (access_key, user_id)

    # Execute the SQL statement
    cursor.execute(sql, values)

    # Commit the changes to the database
    connection.commit()

    # Mapping the user info table

    # data
    # Fethcing the required
    Age = context.user_data["age"]
    Gender = context.user_data["gender"]
    Name = context.user_data["name"]

    sql_q = """
        INSERT INTO user_info(
        user_id, Name, Age, Gender)
        VALUES (%s, %s, %s, %s)
    """
    values = (user_id, Name, Age, Gender)

    # Using cursor to execute the statements
    cursor.execute(sql_q, values)
    # Commit the changes or fetch the results
    connection.commit()

    return True


# Old User

async def addmedauth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide the access key")
    return "addmed"


async def addmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    access_key = update.message.text

    # Executing the stuff
    cursor.execute("SELECT access_key FROM user_id_access_key_map")
    access_key_res = cursor.fetchone()
    try:
        if access_key in access_key_res:
            # Running SQL Query
            cursor.execute(f"""SELECT user_id FROM user_id_access_key_map where access_key = '{access_key}'""")
            user_id = cursor.fetchone()[0]
            context.user_data['user_id'] = user_id

            await update.message.reply_text("Welcome! Good to see you back. I will assist you today in managing your "
                                            "medicine remainders")
            await update.message.reply_text("Please Provide the medicine you want to be reminded of")

            return "medname"

        else:
            await update.message.reply_text("Authentication failed")
    except Exception as e:
        print(e)
        await update.message.reply_text("Please Create the Profile First")

        return await update.message.reply_text("Please Create the Profile First")


async def medname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    medicinename = update.message.text

    context.user_data["medicinename"] = medicinename
    await update.message.reply_text("Kindly let me know how many times a day you have to take the medicine")

    return "medfreq"


async def medfreq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    freq = update.message.text
    freq = int(freq)

    context.user_data["frequency"] = freq

    # await update.message.reply_text("Thank you for providing the Details")
    # await update.message.reply_text("Give me a moment, Let me set the Remainder")
    await update.message.reply_text("Please provide the date of this month at which your remainders should start from ")
    await update.message.reply_text("For e.g. if you want to start from 23-03-2023, just type 23 ")

    return "medfreqdate1"


async def medfreqdate1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_date = update.message.text

    # Write the logic
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    # start_date = f"{start_date}/{current_month}/{current_year}"
    start_date = f"{current_year}-{current_month}-{start_date}"
    start_date = datetime.datetime.strptime(start_date, date_format)
    context.user_data["start_date"] = start_date

    await update.message.reply_text("Please provide the date of this month at which your remainders should end")
    await update.message.reply_text("For e.g. if you want to end at 27-03-2023, just type 27")

    return "medfreqdate2"


async def medfreqdate2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    end_date = update.message.text

    # Write the logic
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    # end_date = f"{end_date}/{current_month}/{current_year}"
    end_date = f"{current_year}-{current_month}-{end_date}"
    end_date = datetime.datetime.strptime(end_date, date_format)
    context.user_data["end_date"] = end_date

    # await update.message.reply_text("Please provide the Time at which you want to be reminded")
    # await update.message.reply_text("For e.g. If you want to be reminded in evening at seven, type in: 19:30")
    await update.message.reply_text("Thanks! Wait a second")

    # Calling SQL table

    # Fetching the values
    user_id = context.user_data['user_id']
    medicinename = context.user_data['medicinename']
    start_date = context.user_data['start_date']
    end_date = context.user_data['end_date']
    freq = context.user_data['frequency']

    sql_q = """INSERT INTO user_med_freq (user_id, start_date, end_date, med, frequency) VALUES (%s, %s, %s, %s, %s)"""
    values = (user_id, start_date, end_date, medicinename, freq)

    cursor.execute(sql_q, values)
    connection.commit()

    return await medfreqtime(update, context)


async def medfreqtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please Provide the Time at which you want to be reminded")

    # Taking the frequency value
    freq = context.user_data["frequency"]
    freq = int(freq)

    # Writing the logic

    if freq == 1:
        return "remindtime"
    elif 1 < freq < 4:
        return "remindtime1"
    else:
        return await update.message.reply_text(
            "Sorry! Probably you choose for more than 3 times remainder a day. Currently we only support one to three "
            "times a day")


async def remindtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remind_time = update.message.text
    # Write the logic
    remind_time = f"{remind_time}:00"
    remind_time = datetime.datetime.strptime(remind_time, "%H:%M:00").time()
    context.user_data["remind_time"] = remind_time

    # Fetching the values
    user_id = context.user_data["user_id"]

    sql_q = """INSERT INTO timeslot_user(user_id, time_remainders) VALUES (%s, %s)"""
    values = (user_id, remind_time)
    cursor.execute(sql_q, values)
    connection.commit()

    # Set your Twilio account SID and auth token
    account_sid = "ACd29a5596f5e738442cdef1db361335fb"
    auth_token = "4bbacb26e7eb77ea7ebae0c5b63210db"

    # Create a Twilio client object

    client = Client(account_sid, auth_token)

    # Fetching the name and med values to insert in the message

    cursor.execute(f"""SELECT name from userinfo WHERE user_id ={context.user_data["user_id"]}""")

    medname = context.user_data["medicinename"]
    name = context.user_data["name"]

    # SQL
    cursor.execute("""WITH RECURSIVE cte_temp AS (
        SELECT user_id, Med, start_date::date, end_date::date, frequency FROM user_med_freq
        UNION ALL
        SELECT user_id, Med, (start_date + INTERVAL '1' DAY)::date, end_date, frequency
        FROM cte_temp
        WHERE (start_date + INTERVAL '1' DAY)::date <= end_date), 
        tabcte AS (
        SELECT user_id, Med, TO_CHAR(start_date, 'DD-MM-YY') AS remainder_date 
        FROM cte_temp
        CROSS JOIN (
        SELECT generate_series(1, 3) AS n
        ) AS counter
        WHERE counter.n <= cte_temp.frequency
        ORDER BY user_id, start_date)
        SELECT t.user_id, t.remainder_date, tu.time_remainders FROM tabcte t
        JOIN timeslot_user tu
        ON t.user_id = tu.user_id""")

    res = cursor.fetchall()

    for x in res:
        each = str(x[1]) + " " + str(x[2])
        dobj = datetime.datetime.strptime(each, "%d-%m-%y %H:%M:%S")
        utctz = datetime.timezone.utc
        dobj = dobj.astimezone(utctz)
        mess = client.messages.create(
            messaging_service_sid="MGa9c4d416d0fc65970e352e0832df1178",
            body=f"Hello {name}!, MediBot here. Your medical assistant helping you managing medication. It is the "
                 f"high time now to take your pill {medname}",
            from_="+13613444759",
            to="+917834937049",
            send_at=dobj,
            schedule_type="fixed"
        )

    return ConversationHandler.END


async def remindtime1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remindtime1 = update.message.text

    # Write the logic
    remindtime1 = f"{remindtime1}:00"
    remindtime1 = datetime.datetime.strptime(remindtime1, "%H:%M:00").time()
    context.user_data["remind_time_two"] = remindtime1

    # Fetching the values
    user_id = context.user_data["user_id"]

    sql_q = """INSERT INTO timeslot_user(user_id, time_remainders) VALUES (%s, %s)"""
    values = (user_id, remindtime1)
    cursor.execute(sql_q, values)
    connection.commit()

    await update.message.reply_text(
        "Please Provide the second time slot of the day at which you want to be reminded for the medicine")

    return "remindtime2"


async def remindtime2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remindtime2 = update.message.text

    # Write the logic
    remindtime2 = f"{remindtime2}:00"
    remindtime2 = datetime.datetime.strptime(remindtime2, "%H:%M:00").time()

    context.user_data["remindtime2"] = remindtime2

    # Fetching the values
    user_id = context.user_data["user_id"]

    sql_q = """INSERT INTO timeslot_user(user_id, time_remainders) VALUES (%s, %s)"""
    values = (user_id, remindtime2)
    cursor.execute(sql_q, values)
    connection.commit()

    # Taking the frequency value
    freq = context.user_data["frequency"]
    freq = int(freq)

    if freq == 2:
        await update.message.reply_text(
            "Thank you for the details")

        return ConversationHandler.END

    else:
        await update.message.reply_text(
            "Please Provide the third time slot of the day at which you want to be reminded for the medicine")

        return "remindtime3"


async def remindtime3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remindtime3 = update.message.text

    # Write the logic
    remindtime3 = f"{remindtime3}:00"
    remindtime3 = datetime.datetime.strptime(remindtime3, "%H:%M:00").time()
    context.user_data["remindtime3"] = remindtime3

    # Fetching the values
    user_id = context.user_data["user_id"]

    sql_q = """INSERT INTO timeslot_user(user_id, time_remainders) VALUES (%s, %s)"""
    values = (user_id, remindtime3)
    cursor.execute(sql_q, values)
    connection.commit()

    await update.message.reply_text(
        "Thank you for the details")

    # Set your Twilio account SID and auth token
    account_sid = "ACd29a5596f5e738442cdef1db361335fb"
    auth_token = "4bbacb26e7eb77ea7ebae0c5b63210db"

    # Create a Twilio client object
    client = Client(account_sid, auth_token)

    # Fetching the name and med values to insert in the message
    medname = context.user_data["medicinename"]
    name = context.user_data["name"]

    # SQL
    cursor.execute("""WITH RECURSIVE cte_temp AS (
    SELECT user_id, Med, start_date::date, end_date::date, frequency FROM user_med_freq
    UNION ALL
    SELECT user_id, Med, (start_date + INTERVAL '1' DAY)::date, end_date, frequency
    FROM cte_temp
    WHERE (start_date + INTERVAL '1' DAY)::date <= end_date), 
    tabcte AS (
    SELECT user_id, Med, TO_CHAR(start_date, 'DD-MM-YY') AS remainder_date 
    FROM cte_temp
    CROSS JOIN (
    SELECT generate_series(1, 3) AS n
    ) AS counter
    WHERE counter.n <= cte_temp.frequency
    ORDER BY user_id, start_date)
    SELECT t.user_id, t.remainder_date, tu.time_remainders FROM tabcte t
    JOIN timeslot_user tu
    ON t.user_id = tu.user_id""")

    res = cursor.fetchall()

    for x in res:
        each = str(x[1]) + " " + str(x[2])
        dobj = datetime.datetime.strptime(each, "%d-%m-%y %H:%M:%S")
        utctz = datetime.timezone.utc
        dobj = dobj.astimezone(utctz)
        mess = client.messages.create(
            messaging_service_sid="MGa9c4d416d0fc65970e352e0832df1178",
            body=f"Hello {name}!, MediBot here. Your medical assistant helping you managing medication. It is the "
                 f"high time now to take your pill {medname}",
            from_="+13613444759",
            to="+917834937049",
            send_at=dobj,
            schedule_type="fixed"
        )



    return ConversationHandler.END


# ConversationHandler for user profile generation
conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", start_command),
        CommandHandler("profile", user_profile_generation),
        CommandHandler("addingmed", addmedauth)
    ],
    states={
        "access_key": [MessageHandler(filters.TEXT, access_key_validation)],
        "name": [MessageHandler(filters.TEXT, name_collection)],
        "age": [MessageHandler(filters.TEXT, age_collection)],
        "gender": [MessageHandler(filters.TEXT, gender_collection)],
        "addmed": [MessageHandler(filters.TEXT, addmed)],
        "medname": [MessageHandler(filters.TEXT, medname)],
        "medfreq": [MessageHandler(filters.TEXT, medfreq)],
        "medfreqdate1": [MessageHandler(filters.TEXT, medfreqdate1)],
        "medfreqdate2": [MessageHandler(filters.TEXT, medfreqdate2)],
        "remindtime": [MessageHandler(filters.TEXT, remindtime)],
        "remindtime1": [MessageHandler(filters.TEXT, remindtime1)],
        "remindtime2": [MessageHandler(filters.TEXT, remindtime2)],
        "remindtime3": [MessageHandler(filters.TEXT, remindtime3)]
    },
    fallbacks=[],  # No fallbacks in this example
)

# Run Program
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # Add the conversation handler to the application
    app.add_handler(conversation_handler)

    print("Polling...")
    # Run the bot
    app.run_polling(poll_interval=5)

