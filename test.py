import duckdb
import ttkbootstrap as tb
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tableview import Tableview
from PIL import ImageTk, Image
import scrape
from ttkbootstrap.tooltip import ToolTip

Done = 0
All = 0
Question = "  "
Answers = {
    "Answer1": (1, True),
    "Answer2": (2, False),
    "Answer3": (3, False),
    "Answer4": (4, False),
}
image_location = ""
con = duckdb.connect("theory.db")

check = "Select count(*) from information_schema.tables"
con.execute(check)
rslt = con.fetchone()
print(rslt[0])
if rslt[0] == 0:
    con.execute(
        "CREATE OR REPLACE TABLE Questions (Rowid int, Question VARCHAR, Answer1 VARCHAR, Answer1_value bool, Answer2 VARCHAR, Answer2_value bool, Answer3 VARCHAR, Answer3_value bool, Answer4 VARCHAR, Answer4_value bool, Image VARCHAR, Correct bool, Type VARCHAR);"
    )

root = tb.Window()
Top = tb.Toplevel()
style = tb.Style(theme="cyborg")
light = 1

root.title("תאוריה")
root.iconbitmap("images.ico")
root.minsize(400, 200)
root.place_window_center()
root.geometry("")

Top.title("תאוריה")
Top.iconbitmap("images.ico")
Top.minsize(750, 370)
Top.place_window_center()
Top.geometry("")
# print(f"Original Q: {Question}")
# print(f"RTL Q: {rtl(Question)}")


def rtl(text="שלום. welcome. מה שלומכם?"):

    new_text = []
    # list to hold each sentence

    end_character_number = len(text) - 1
    end_char = end_character_number

    if text[end_char] == "?" or text[end_char] == "!" or text[end_char] == ".":
        new_text.append(text[end_char])  # adds final punctuation first
        text = text[:end_char]  # removes final punctuation from left-to-right text

    right_to_left_checker = end_char - 1
    rtl_checker = right_to_left_checker

    while rtl_checker >= 0:
        if (
            text[rtl_checker] == "?"
            or text[rtl_checker] == "!"
            or text[rtl_checker] == "."
            or text[rtl_checker] == ":"
        ):
            sentence = text[rtl_checker + 1 :].strip()
            new_text.append(sentence)  # adds each sentence in right-to-left order
            new_text.append(" " + text[rtl_checker])  # add punctuation and space after
            text = text[:rtl_checker]  # removes sentence from left-to-right text
        if rtl_checker == 0:
            new_text.append(text)  # adds final sentence in right-to-left order
            text = text[:rtl_checker]  # removes final sentence from left-to-right text
        rtl_checker = (
            rtl_checker - 1
        )  # moves punctuation checker one place right-to-left

    right_to_left_sentence = ""
    rtl_sent = right_to_left_sentence

    for part in new_text:
        rtl_sent = rtl_sent + part  # creates new right-to-left sentence

    return rtl_sent


# Light/Dark toggle
def style_toggle():
    """
    Toggle light/dark mode
    :return: None
    """
    global light
    if light == 1:
        tb.Style(theme="yeti")
        light = 0
    else:
        tb.Style(theme="cyborg")
        light = 1


def submit():

    result = radios.get()
    print(f"This is the result: {result}")
    if result == "empty":
        toast = ToastNotification(
            title="לא בחרת אפשרות",
            message="נא לבחור אפשרות כדי להתקדם",
            duration=3000,
            icon="*",
            bootstyle="danger",
        )
        toast.show_toast()
    elif result == "True":
        toast = ToastNotification(
            title="תשובה נכונה",
            message="אפשר להמשיך",
            duration=3000,
            icon="@",
            bootstyle="success",
        )
        toast.show_toast()
        next_question(True)
    else:
        toast = ToastNotification(
            title="תשובה לא נכונה",
            message="נחזור לשאלה בהמשך",
            duration=3000,
            icon="!",
            bootstyle="warning",
        )
        toast.show_toast()

        next_question(False)


def next_question(correct):
    query_questions(combo.get())
    print(Answers.items())
    for values, text in Answers.items():
        print(text[0])
        radios.update_label(text[0] - 1, values, text[1])
    QuestionLabel.config(text=Question)
    q_img.update()
    radios.deselect()
    if correct:
        update_query = f"Update Questions Set Correct = True where Rowid = {ID}"
        con.execute(update_query)
        statists()
        tbl.delete_row(
            0,
        )
        tbl.insert_row(values=[Done, All])
        tbl.load_table_data()


def statists():
    global All, Done
    count_query = f"Select Count(*) as Cnt_all, sum(case when Correct then 1 else 0 end) as cnt_done from questions where type = '{combo.get()}'"
    con.execute(count_query)
    cnt_results = con.fetchone()
    All, Done = cnt_results


def query_questions(type):
    global Answers, ID, Question, image_location, prev_result
    query = f"Select * from questions where not Correct and type = '{type}' ORDER BY uuid() limit 1"
    con.execute(query)
    results = con.fetchone()
    print(results)
    (
        ID,
        Question,
        Answer1,
        CA1,
        Answer2,
        CA2,
        Answer3,
        CA3,
        Answer4,
        CA4,
        image_location,
        prev_result,
        type,
    ) = results
    Answers = {
        Answer1: (1, CA1),
        Answer2: (2, CA2),
        Answer3: (3, CA3),
        Answer4: (4, CA4),
    }
    print(Question)


class image:
    def __init__(self):

        if image_location != "":
            print(image_location)
            self.image_file = ImageTk.PhotoImage(Image.open(f"{image_location}"))
            self.img = tb.Label(Top, image=self.image_file)
            self.img.grid(row=6, columnspan=2)
        else:
            self.img = tb.Label(Top)

    def update(self):
        if image_location != "":
            self.image_file = ImageTk.PhotoImage(Image.open(f"{image_location}"))
            # img = tb.Label(Top, image=image_file).grid(row=6, columnspan=2)
            self.img.config(image=self.image_file)
            self.img.grid(row=6, columnspan=2)
        else:
            self.img.grid_forget()


class r_buttons:
    def __init__(self, Top):
        self.v = tb.StringVar(Top, "0")
        self.button_list = []
        self.button_labels_list = []
        for text, value in Answers.items():
            rd = tb.Radiobutton(Top, variable=self.v, value=value[0]).grid(
                row=value[0] + 1, column=2, padx=15, pady=10
            )
            if value[1] == True:
                self.correct = str(value[0])
            self.button_list.append(rd)
            rd_label = tb.Label(
                Top, text=rtl(text), anchor="e", width=80, name="btn" + str(value[0])
            )
            rd_label.grid(row=value[0] + 1, column=1, padx=20)
            self.button_labels_list.append(rd_label)

    def update_label(self, idx, txt, val):
        self.button_labels_list[idx].config(text=txt)
        if val == True:
            self.correct = str(idx + 1)

    def get(self):
        tv = self.v.get()
        print(f"This is v: {tv}")
        if tv == "None" or tv == "0":
            result = "empty"
        elif tv == self.correct:
            result = "True"
        else:
            result = "False"
        return result

    def deselect(self):
        self.v.set("0")


def Check_database(type):
    query = f"Select count(*) from questions where type = '{type}'"
    con.execute(query)
    return con.fetchone()


def update_q_label(type):
    if len(type) > 0:
        num_q = Check_database(type)
        print(num_q[0])
        num_qs_label.config(text=f"מספר השאלות במאגר כרגע: {num_q[0]}")
        button_reload["state"] = "normal"
        if num_q[0] > 0:
            button_questions["state"] = "normal"
            button_reset["state"] = "normal"
        else:
            button_questions["state"] = "disabled"
            button_reset["state"] = "disabled"
        print(types[type])


def reload_questions(type, url):
    del_query = f"Delete from questions where type = '{type}'"
    print(del_query)
    con.execute(del_query)
    scrape.reload(type, url)
    update_q_label(type)


def load_question_window():
    statists()
    tbl.delete_row(
        0,
    )
    tbl.insert_row(values=[Done, All])
    tbl.load_table_data()
    Top.deiconify()
    print("***")
    next_question(False)


def donothing():
    """
    Empty func for X button repression
    :return: pass
    """
    pass


def reset_questions():
    query = f"Update questions set Correct = False where type = '{combo.get()}'"
    con.execute(query)


ld_check = tb.Checkbutton(Top, command=style_toggle, style="Squaretoggle.Toolbutton")
ld_check.grid(row=12, column=0, padx=10, pady=10)

submit_btn = tb.Button(Top, text="שלח", command=submit).grid(
    row=8, columnspan=2, pady=20
)

exit_btn = tb.Button(Top, text="יציאה מהשאלון", command=Top.withdraw)
exit_btn.grid(row=9, columnspan=2)

rd = [(Done, All)]

tbl = Tableview(
    master=Top,
    coldata=["תשובות נכונות", 'סה"כ שאלות'],
    rowdata=rd,
    height=1,
    pagesize=2,
    autofit=True,
)
tbl.grid(row=15, columnspan=2)


QuestionLabel = tb.Label(Top, text=rtl(Question), font=("sans", "15", "bold"))

QuestionLabel.grid(row=1, columnspan=2)
radios = r_buttons(Top)
q_img = image()
Top.protocol("WM_DELETE_WINDOW", donothing)
Top.withdraw()
# print(list(scrape.get_list(scrape.url).keys()))
types = scrape.get_list(scrape.url)
type_list = list(types.keys())
num_qs_label = tb.Label(root, text="")
num_qs_label.grid(row=3, columnspan=3)
title_label = tb.Label(root, text="נא לבחור סוג רשיון")
title_label.grid(row=1, columnspan=3)
combo = tb.Combobox(root, values=type_list)
combo.grid(row=2, columnspan=3)
button_reload = tb.Button(
    root,
    text="טעינה מחדש של שאלות המאגר",
    command=lambda: reload_questions(combo.get(), types[combo.get()]),
)
button_reload.grid(row=5, column=1, padx=15)
button_reload["state"] = "disabled"
button_questions = tb.Button(root, text="למעבר לשאלות", command=load_question_window)
button_questions.grid(row=5, column=2)
button_questions["state"] = "disabled"
combo.bind("<<ComboboxSelected>>", lambda _: update_q_label(combo.get()))
button_reset = tb.Button(root, text="איפוס שאלות", command=reset_questions)
button_reset.grid(row=6, columnspan=3, pady=15)
button_reset["state"] = "disabled"

ToolTip(
    button_reload,
    text="טעינה מחדש של השאלות עלול לקחת כמה דקות",
)

ToolTip(button_reset, text="מאפס רישום של שאלות שנענו באופן נכון")

root.mainloop()
print(rtl())
