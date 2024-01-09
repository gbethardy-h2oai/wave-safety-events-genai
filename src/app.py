import os
import toml
import pandas as pd
from loguru import logger
from h2ogpte import H2OGPTE
from h2o_wave import Q, app, handle_on, main, on, ui, data, run_on, copy_expando
from .event_analytics import prepare_text, classify_events, classify_report



@app("/")
async def serve(q: Q):
    #print(q.args)
    #print(q.client)
    logger.debug(q.args)
    copy_expando(q.args, q.client)  # Save any UI responses of the User to their session

    if not q.client.initialized:
        # First time a browser comes to the app
        await init(q)
        q.client.initialized = True

    elif q.args.file_upload:
        q.args.sample_dataset = None
        q.client.file_upload = True

        # Save location of data and dataframe to use in the app
        q.client.file_path = await q.site.download(
            url=q.args.file_upload[0], path=q.app.data_save_location
        )
        q.client.original_data = pd.read_csv(
            q.client.file_path, encoding_errors="ignore"
        )

        # Show the upload data page again
        await nav_import(q)


    elif q.args.sample_dataset:
        q.args.file_upload = None
        q.client.sample_dataset = True

        q.client.file_path = os.path.join(q.app.data_save_location, "safety_events_demo_small.csv")
        q.client.original_data = pd.read_csv(
            q.client.file_path, encoding_errors="ignore"
        )

        #Show the upload data page again
        await nav_import(q)


    elif q.args.preview_data:
        q.client.preview_data = q.args.preview_data
        q.client.preview_row = q.args.preview_data[0]
        #print(f"table preview data: {q.args.preview_data[0]} ")
        #print(f"table preview data: {q.client.original_data.iloc[int(q.args.preview_data[0])]} ")
        q.client.current_event_description = q.client.original_data.iloc[int(q.args.preview_data[0])]['Event_Description']
        q.client.current_answer = q.client.original_data.iloc[int(q.args.preview_data[0])]['h2oGPTe_Response']

        await edit_data(q)


    elif q.args.data_details_cmd:
        logger.debug(f"data_details_cmd selected row: {q.args.data_details_cmd[0]}")
        #q.client.prompt_select_table = q.args.prompt_select_table
        q.client.preview_row = q.args.data_details_cmd[0]
        q.client.current_event_description = q.client.original_data.iloc[int(q.args.data_details_cmd[0])]['Event_Description']
        q.client.current_answer = q.client.original_data.iloc[int(q.args.data_details_cmd[0])]['h2oGPTe_Response']

        await edit_data(q)


    elif q.args.data_email_cmd:
        logger.debug(f"data_email_cmd selected row: {q.args.data_email_cmd[0]}")
        #q.client.prompt_select_table = q.args.prompt_select_table
        q.client.preview_row = q.args.data_email_cmd[0]
        q.client.current_event_description = q.client.original_data.iloc[int(q.args.data_email_cmd[0])]['Event_Description']
        q.client.current_answer = q.client.original_data.iloc[int(q.args.data_email_cmd[0])]['h2oGPTe_Response']

        await edit_email(q)


    elif q.args.data_prompt_cmd:
        logger.debug(f"data_prompt_cmd selected row: {q.args.data_prompt_cmd[0]}")
        #q.client.prompt_select_table = q.args.prompt_select_table
        #q.client.preview_row = q.args.data_email_cmd[0]
        #q.client.current_event_description = q.client.original_data.iloc[int(q.args.data_email_cmd[0])]['Event_Description']
        #q.client.current_answer = q.client.original_data.iloc[int(q.args.data_email_cmd[0])]['h2oGPTe_Response']

        await nav_catalog(q)


    elif q.args.save_preview_edits:
        q.client.original_data.at[int(q.client.preview_row), 'h2oGPTe_Response'] = q.args.edited_response
        q.client.original_data.at[int(q.client.preview_row), 'Event_Description'] = q.args.edited_description
        await nav_import(q)

    elif q.args.send_preview_email:
        q.client.send_preview_email = q.args.send_preview_email
        await edit_email(q)

    elif q.args.cancel_preview_edits:
        q.client.cancel_preview_edits = q.args.cancel_preview_edits
        await nav_import(q)


    elif q.args.cancel_email_edits:
        q.client.cancel_email_edits = q.args.cancel_email_edits
        await nav_import(q)

    elif q.args.save_email_edits:
        q.client.original_data.at[int(q.client.preview_row), 'h2oGPTe_Email_Response'] = q.args.edited_email
        await nav_import(q)


    elif q.args.send_email_edits:
        q.client.original_data.at[int(q.client.preview_row), 'h2oGPTe_Email_Response'] = q.args.edited_email
        email_sent(q)
        await nav_import(q)


    elif q.args.prompt_table:
        q.client.prompt_table = q.args.prompt_table
        q.client.prompt_row = q.args.prompt_table[0]
        #print(f"table prompt data: {q.args.prompt_table[0]} ")
        #print(f"table prompt row: {q.client.prompt_catalog.iloc[int(q.args.prompt_table[0])]} ")

        await edit_prompt(q)


    elif q.args.edit_catalog_cmd:
        #q.client.prompt_table = q.args.prompt_table
        q.client.prompt_row = q.args.edit_catalog_cmd[0]
        # print(f"table prompt data: {q.args.prompt_table[0]} ")
        # print(f"table prompt row: {q.client.prompt_catalog.iloc[int(q.args.prompt_table[0])]} ")

        await edit_prompt(q)


    elif q.args.save_prompt_edits:
        #print(f"in save prompt:")

        # If setting new prompt default=True, set all other prompt to default=False
        if q.args.default_checkbox == True:
            print("checkbox default is true")
            if q.args.prompt_type_dropdown == 'classification':
                print("dropdown type is classification")
                q.client.prompt_catalog.loc[q.client.prompt_catalog['Prompt_Type'] == 'classification', 'Default'] = False
            else:
                q.client.prompt_catalog.loc[q.client.prompt_catalog['Prompt_Type'] == 'email', 'Default'] = False

        # Get the max Prompt_ID for the Prompt_type for the new entry in the Prompt Catalog
        #max_classification_prompt_id = q.client.prompt_catalog[q.client.prompt_catalog['Prompt_Type'] =='classification']['Prompt_ID'].max()
        #max_email_prompt_id = q.client.prompt_catalog[q.client.prompt_catalog['Prompt_Type'] == 'email']['Prompt_ID'].max()
        #print (f"max email prompt ID: {max_email_prompt_id}")
        #current_prompt_id = q.client.prompt_catalog.iloc[int(q.client.prompt_row)]['Prompt_ID'].max()
        #print(f"max current prompt ID: {current_prompt_id}")
        # if q.client.prompt_catalog.iloc[int(q.client.prompt_row)]['Prompt_Type'] == 'classification':
        #     if current_prompt_id == max_classification_prompt_id:
        #         new_prompt_id = current_prompt_id + 1
        #     else:
        #         new_prompt_id = int(max_email_prompt_id) + 1
        # else:
        #     if current_prompt_id == max_email_prompt_id:
        #         new_prompt_id = current_prompt_id + 1
        #     else:
        #         new_prompt_id = int(max_classification_prompt_id) + 1
        new_prompt_id = int(q.client.prompt_catalog['Prompt_ID'].max()) + 1
        #print(f"new prompt ID: {new_prompt_id}")

        # # Add new prompt row to the Prompt Catalog
        new_row = { 'Prompt_ID': [(int(new_prompt_id))],
                    'Prompt_Type': [q.args.prompt_type_dropdown],
                    'Prompt_Text': [q.args.edited_prompt],
                    'Default': [q.args.default_checkbox]
                    }
        new_row_df = pd.DataFrame(new_row)
        new_row_df = new_row_df.rename(index={0: new_prompt_id})
        q.client.prompt_catalog = pd.concat([q.client.prompt_catalog, new_row_df])
        q.client.prompt_catalog = q.client.prompt_catalog.reset_index(drop=True)

        await nav_catalog(q)


    elif q.args.cancel_prompt_edits:
        await nav_catalog(q)



    elif q.args.generate_response:
        logger.debug(f"Generating new response")

        q.client.current_answer = await q.run(get_llm_response, q, q.client.current_prompt_text)

        await edit_data(q)




    elif q.args.prompt_select_table:
        q.client.prompt_select_table = q.args.prompt_select_table
        q.client.prompt_select_row = q.args.prompt_select_table[0]
        #print(f"select table prompt data: {q.args.prompt_select_table[0]} ")
        #print(f"select table prompt row: {q.client.prompt_catalog.iloc[int(q.args.prompt_select_table[0])]} ")
        q.client.current_prompt_text = q.client.prompt_catalog.iloc[int(q.args.prompt_select_table[0])]['Prompt_Text']
        q.client.current_prompt_text = str(q.client.current_prompt_text).replace('<event_description>', q.client.current_event_description)

        await edit_data(q)




    elif q.args.get_catalog_prompt:
        q.client.current_prompt_text = q.client.prompt_catalog.iloc[int(q.args.prompt_select_table[0])]['Prompt_Text']
        logger.debug(f"Getting catalog prompt")
        print(f"Getting catalog prompt")

        await edit_data(q)








    else:
        # Other browser interactions
        await run_on(q)

    await q.page.save()





async def init(q: Q) -> None:
    q.client.cards = []

    if not q.app.initialized:
        logger.info("Initializing the app")
        q.app.toml = toml.load("app.toml")

        # Set the h2oGPTe variables
        q.app.remote_address = os.getenv("H2OGPTE_ADDRESS", "https://playground.h2ogpte.h2o.ai")
        #q.app.api_key = os.getenv("H2OGPTE_API_KEY", "")
        q.app.api_key = "sk-6We9NYJfXbCICIOEwQdhnu972qMgAVwhAETiRRujtsZ3Yz7P"
        q.app.collection_name = os.getenv("COLLECTION_NAME", "Safety Events")
        #print(f"h2ogpte api key: {q.app.api_key}")

        # All user data is saved in the save folder
        q.app.data_save_location = "./data/"
        if not os.path.exists(q.app.data_save_location):
            os.makedirs(q.app.data_save_location)

        q.app.initialized = True


    # Upload the home page image to the server once to use for all users
    (q.app.header_image,) = await q.site.upload(["h2o_health.png"])
    # print(f"image uploaded: {q.app.header_image}")
    q.app.load_image, = await q.site.upload(['giphy_load2.gif'])
    # print(f"init: chat image uploaded: {q.app.load_image}")

    # Read in the Prompt Catalog
    q.client.prompt_catalog_path = os.path.join(q.app.data_save_location, "prompt_catalog.csv")
    q.client.prompt_catalog = pd.read_csv(
        q.client.prompt_catalog_path, encoding_errors="ignore",
        sep='|',
        engine='python'
    )
    q.client.prompt_catalog = q.client.prompt_catalog.reset_index()
    print(f"init prompt catalog: q.client.prompt_catalog.head()")

    q.client.chat_length = 0
    q.client.current_prompt_text = ""
    q.client.new_response = ""


    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone("main"),
                        ],
                    ),
                    ui.zone(name="buttons"),
                    ui.zone(name="footer"),
                ],
            )
        ],
    )
    q.page["header"] = ui.header_card(
        box="header",
        title="Patient and Employee Healthcare Safety Event Classifier",
        subtitle="Powered by Open Source and Enterprise H2oGPTe",
        image="https://cloud.h2o.ai/logo.svg",
    )
    q.page["navigation"] = ui.nav_card(
        box=ui.box("navigation", size=0),
        items=[
            ui.nav_group(
                label="Workflow Menu",
                items=[
                    ui.nav_item("nav_home", "Home", "Home"),
                    ui.nav_item("nav_import", "Safety Event Upload/Preview", "TableGroup"),
                    ui.nav_item("nav_import", "Human-in-the-loop Review", "Contact"),
                    ui.nav_item("nav_import", "Edit/Send Autogenerated Email", "EditMail"),
                    ui.nav_item("nav_catalog", "Manage Prompt Catalog", "ReviewRequestSolid"),
                    ui.nav_item("nav_chat", "AdHoc Chat", "Chat"),
                    ui.nav_item("nav_home", "EXPERT - Save Data for Fine-Tuning", "Download"),
                ],
            ),
        ],
    )
    q.page["footer"] = ui.footer_card(
        box="footer", caption="Made with 💛 using [H2O Wave](https://wave.h2o.ai)."
    )

    await nav_home(q)



async def edit_layout(q: Q) -> None:
    q.client.cards = []


    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone(name="main",
                                    zones=[ui.zone(name="main_0", direction="column", size="50%"),
                                           ui.zone(name="main_1", direction="column", size="50%")]

                            ),
                        ],
                    ),
                    ui.zone(name="footer"),
                ],
            )
        ],
    )
    q.page["header"] = ui.header_card(
        box="header",
        title="Patient and Employee Healthcare Safety Event Classifier",
        subtitle="Powered by Open Source and Enterprise H2oGPTe",
        image="https://cloud.h2o.ai/logo.svg",
    )
    q.page["navigation"] = ui.nav_card(
        box=ui.box("navigation", size=0),
        items=[
            ui.nav_group(
                label="Workflow Menu",
                items=[
                    ui.nav_item("nav_home", "Home", "Home"),
                    ui.nav_item("nav_import", "Event Upload/Review", "TableGroup"),
                ],
            ),
        ],
    )
    q.page["footer"] = ui.footer_card(
        box="footer", caption="Made with 💛 using [H2O Wave](https://wave.h2o.ai)."
    )

    await edit_data(q)




@on()
async def chatbot(q):
    print("chabot begin ...")
    starting_chat_length = q.client.chat_length
    q.client.chat_length += 2

    q.page['chatbot'].data += [q.client.chatbot, True]
    q.page['chatbot'].data += ["<img src='{}' height='200px'/>".format(q.app.load_image), False]

    await q.page.save()

    logger.debug("chatbot: calling get_llm_response")
    print("chatbot: calling get_llm_response")
    bot_res = await q.run(get_llm_response, q, q.client.chatbot)

    diff = q.client.chat_length - starting_chat_length - 1
    q.page['chatbot'].data[-diff] = [bot_res, False]




def get_llm_response(q, user_message):
    logger.debug("get_llm_response: begin")
    print("get_llm_response: begin")
    q.app.h2ogpte_client = H2OGPTE(address=q.app.remote_address, api_key=q.app.api_key)

    collection_id = None
    recent_collections = q.app.h2ogpte_client.list_recent_collections(0, 1000)
    for c in recent_collections:
        if c.name == q.app.collection_name and c.document_count:
            collection_id = c.id
            break
    try:
        logger.debug(user_message)
        #print(user_message)

        chat_session_id = q.app.h2ogpte_client.create_chat_session(collection_id=collection_id)
        with q.app.h2ogpte_client.connect(chat_session_id) as session:
            reply = session.query(
                message=user_message,
                timeout=16000,
            )

        response = reply.content
        logger.debug(response)
        #print(response)
        return response.strip()

    except Exception as e:
        logger.error(e)
        #print(e)
        return ""





@on()
async def nav_home(q: Q):
    clear_cards(q)
    q.page["navigation"].value = "nav_home"

    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone("main"),
                        ],
                    ),
                    ui.zone(name="footer"),
                ],
            )
        ],
    )

    #(q.app.header_image,) = await q.site.upload(["safety-logo-500px.png"])
    #print(f"image uploaded: {q.app.header_image}")
    q.page["home"] = ui.form_card(
        box="main",
        items=[
            #ui.text(f'<img src="{q.app.header_image}">'),
            ui.text_xl("Review, Manage, and Classify Healthcare Safety Events:"),
            ui.text("1. Upload a dataset of event descriptions with h2oGPTe GenAI classifications/explanations"),
            ui.text("2. Human-in-the-loop, review and edit or accept the classification for each event"),
            ui.text("3. Human-in-the-loop, generate a new h2oGPTe response for any event"),
            ui.text("4. Automatically generate and optionally edit an email for any event"),
            ui.text("5. Create and edit new prompts in the Prompt Catalog"),
            #ui.message_bar(
            #    type="info", text="It may take a few minutes to process your data."
            #),
            ui.text(f'<center><img src="{q.app.header_image}"></center>'),
        ],
    )
    q.client.cards.append("home")


@on()
async def nav_import(q: Q):
    clear_cards(q)
    q.page["navigation"].value = "nav_import"

    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone("main"),
                        ],
                    ),
                    ui.zone(name="footer"),
                ],
            )
        ],
    )

    commands = [
        ui.command(name='data_details_cmd', label='Details', icon='Info'),
        ui.command(name='data_email_cmd', label='Email', icon='Mail'),
        ui.command(name='data_prompt_cmd', label='Prompt', icon='QueryList'),
        #ui.command(name='data_h2ogpte_cmd', label='h2oGPTe', icon='Chat'),
    ]


    # If a dataset has already been uploaded, lets show it on this page
    header = ui.text(" ")
    table = ui.text(" ")
    if q.client.original_data is not None:
        print(q.client.original_data.head())
        header = ui.text_l("Review")
        table = ui.table(
            name="preview_data",
            columns=[
                ui.table_column(col, col.replace("_", " "), cell_overflow='tooltip', link=True, searchable=True, sortable=True) if col=='File_ID'
                else ui.table_column(col, col.replace("_", " "), sortable=True, cell_overflow='tooltip')
                for col in q.client.original_data[['File_ID', 'Event_Date', 'Event_Description', 'h2oGPTe_Response']].columns
            ] + [ui.table_column(name='actions', label='Actions', cell_type=ui.menu_table_cell_type(name='commands', commands=commands))],
            rows=[
                ui.table_row(
                    str(i),
                    [
                        str(q.client.original_data[['File_ID', 'Event_Date', 'Event_Description', 'h2oGPTe_Response']].loc[i, col])
                        for col in q.client.original_data[['File_ID', 'Event_Date', 'Event_Description', 'h2oGPTe_Response']].columns
                    ],
                )
                for i in range(len(q.client.original_data[['File_ID', 'Event_Date', 'Event_Description', 'h2oGPTe_Response']]))
            ],
        )

    q.page["import"] = ui.form_card(
        box="main",
        items=[ui.button(name='sample_dataset', label='Import Demo Data', primary=True),
               ui.file_upload(
                    name="file_upload",
                    label="Import CSV File",
                    compact=False,
                    multiple=False,
                    file_extensions=["csv"],
                    height='200px',
                    width='200px'
                    #max_file_size=50,
               ),
               header,
               table,
              ],
    )
    q.client.cards.append("import")



@on()
async def edit_data(q: Q):
    clear_cards(q)
    q.page["navigation"].value = "edit_data"

    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone(name="main", direction=ui.ZoneDirection.ROW,
                                    zones=[ui.zone(name="main_0", size="50%"),
                                           ui.zone(name="main_1", size="50%")]

                                    ),
                        ],
                    ),
                    ui.zone(name="buttons"),
                    ui.zone(name="footer"),
                ],
            )
        ],
    )

    q.page["edit_data0"] = ui.form_card(
        box="main_0",
        items=[ui.text_xl('Event Detail'),
               ui.textbox(name='edited_description',
                          label='Event Description',
                          multiline=True,
                          readonly=True,
                          #value=q.client.original_data.iloc[int(q.args.preview_data[0])]['Event_Description']),
                          value = q.client.original_data.iloc[int(q.client.preview_row)]['Event_Description']),

        ]
    )

    q.page["edit_data1"] = ui.form_card(
        box="main_1",
        items=[ui.text_xl('Human-in-the-loop - Edit or Generate New Response'),
               ui.textbox(name='edited_response',
                          label='Edit h2oGPTe Response',
                          multiline=True,
                          readonly=False,
                            value = q.client.current_answer),
               ui.links(label='', items=[
                   ui.link(label='Exlpore Response References at h2oGPT Enterprise', path='https://playground.h2ogpte.h2o.ai/', target='_blank')]),
               ui.text_xl(' '),
               ui.text_xl(' '),
               ui.separator(label=''),
               ui.text_xl(' '),
               ui.text_xl(' '),
               ui.text_l('Generate a New Response'),
               ui.text('Note: Prompts can created/edited in the Prompt Catalog Manager'),
               ui.table(
                   name="prompt_select_table",
                   columns=[
                       ui.table_column(col, col.replace("_", " "), cell_overflow='tooltip', link=True,
                                       searchable=True,
                                       sortable=True) if col == 'Prompt_ID'
                       else ui.table_column(col, col.replace("_", " "), sortable=True, cell_overflow='tooltip')
                       for col in
                       q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].columns
                   ],
                   rows=[
                       ui.table_row(
                           str(i),
                           [
                               str(q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].loc[
                                       i, col])
                               for col in
                               q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].columns
                           ],
                       )
                       for i in
                       range(len(q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']]))
                   ],
                   value='0'
               ),
               ui.textbox(name='edited_row_prompt',
                          label='Prompt',
                          multiline=True,
                          readonly=True,
                          # value=q.client.prompt_catalog.iloc[int(q.client.prompt_select_row)]['Question']),
                          value=q.client.current_prompt_text),
               ui.button(name="get_catalog_prompt", label="Select Prompt from Catalog", primary=True),
               ui.button(name="generate_response", label="Generate New Response", primary=True),
        ]
    )

    q.page["edit_data2"] = ui.form_card(
        box="buttons",
        items=[ui.buttons(justify='end', items=[
                    ui.button(name="cancel_preview_edits", label="Cancel and Return to Preview", primary=True),
                    ui.button(name="save_preview_edits", label="Save Edited Event", primary=True),
                    ui.button(name="send_preview_email", label="Send Email", primary=True)
                    ])
        ]
    )

    q.client.cards.append("edit_data0")
    # q.client.cards.append("edit_data1")
    # q.client.cards.append("edit_data2")



@on()
async def edit_email(q: Q):
    clear_cards(q)
    q.page["navigation"].value = "edit_email"

    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone("main"),
                        ],
                    ),

                    ui.zone(name="footer"),
                ],
            )
        ],
    )

    q.page["edit_email"] = ui.form_card(
        box="main",
        items=[ui.textbox(name='edited_email',
                          label='Edit Automated Email',
                          multiline=True,
                          readonly=False,
                          value=q.client.original_data.iloc[int(q.client.preview_row)]['h2oGPTe_Email_Response']),
               ui.button(name="cancel_email_edits", label="Cancel and Return to Preview", primary=True),
               ui.button(name="save_email_edits", label="Save Edited Email", primary=True),
               ui.button(name="send_email_edits", label="Send", primary=True),
        ]
    )
    q.client.cards.append("edit_email")



@on()
async def edit_prompt(q: Q):
    clear_cards(q)
    q.page["navigation"].value = "edit_prompt"

    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone("main"),
                        ],
                    ),

                    ui.zone(name="footer"),
                ],
            )
        ],
    )

    q.page["edit_prompt"] = ui.form_card(
        box="main",
        items=[ui.textbox(name='edited_prompt',
                          label='Edit Prompt',
                          multiline=True,
                          readonly=False,
                          value=q.client.prompt_catalog.iloc[int(q.client.prompt_row)]['Prompt_Text']),
               ui.dropdown(name='prompt_type_dropdown', label='Prompt Type', required=True,
                    choices=[
                        ui.choice(name='classification', label='classification'),
                        ui.choice(name='email', label='email')
                    ],
                    value=q.client.prompt_catalog.iloc[int(q.client.prompt_row)]['Prompt_Type']),
               ui.checkbox(name='default_checkbox', label='Default?', value= bool(q.client.prompt_catalog.iloc[int(q.client.prompt_row)]['Default'])),
               ui.button(name="cancel_prompt_edits", label="Cancel and Return to Prompt Catalog", primary=True),
               ui.button(name="save_prompt_edits", label="Save as New Prompt", primary=True),
        ]
    )
    q.client.cards.append("edit_prompt")



@on()
async def nav_chat(q: Q):
    clear_cards(q)
    q.page["navigation"].value = "nav_chat"

    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone("main"),
                        ],
                    ),

                    ui.zone(name="footer"),
                ],
            )
        ],
    )

    # q.page["chat_example"] = ui.form_card(
    #     box="main",
    #     name="chat_example",
    #     items=[ui.text_xl(name='Chat with the Safety Event Classification Guide Document'),
    #         ui.text_l(name='Example: What is a moderate healthcare safety event'),
    #     ]
    # )

    q.page["chatbot"] = ui.chatbot_card(
        box="main",
        name='chatbot',
        data=data(fields='content from_user', t='list'),
        #generating=True,
        events=['scroll']
     )

    #q.client.cards.append("chat_example")
    q.client.cards.append("chatbot")



@on()
async def edit_response(q: Q):
    clear_cards(q)
    q.page["navigation"].value = "edit_response"

    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone("main"),
                        ],
                    ),

                    ui.zone(name="footer"),
                ],
            )
        ],
    )

    q.page["edit_response"] = ui.form_card(
        box="main",
        items=[
            ui.table(
                name="prompt_select_table",
                columns=[
                    ui.table_column(col, col.replace("_", " "), cell_overflow='tooltip', link=True,
                                    searchable=True,
                                    sortable=True) if col == 'Prompt_ID'
                    else ui.table_column(col, col.replace("_", " "), sortable=True, cell_overflow='tooltip')
                    for col in
                    q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].columns
                ],
                rows=[
                    ui.table_row(
                        str(i),
                        [
                            str(q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].loc[
                                    i, col])
                            for col in
                            q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].columns
                        ],
                    )
                    for i in
                    range(len(q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']]))
                ],
                value='0'
            ),
            ui.textbox(name='edited_row_prompt',
                          label='Prompt',
                          multiline=True,
                          readonly=True,
                          #value=q.client.prompt_catalog.iloc[int(q.client.prompt_select_row)]['Question']),
                          value = q.client.current_prompt_text),
               ui.button(name="get_catalog_prompt", label="Select Prompt from Catalog", primary=True),
               ui.button(name="generate_row_prompt_response", label="Generate New Response", primary=True),
               ui.textbox(name='edited_row_response',
                          label='New Response',
                          multiline=True,
                          readonly=False,
                          # value=q.client.prompt_catalog.iloc[int(q.client.prompt_select_row)]['Question']),
                          value=q.client.current_answer),
               ui.button(name="save_row_prompt_edits", label="Save New Response", primary=True),
               ui.button(name="cancel_row_prompt_edits", label="Cancel and Return", primary=True),
        ]
    )
    q.client.cards.append("edit_response")





@on()
async def nav_catalog(q: Q):
    clear_cards(q)
    q.page["navigation"].value = "nav_catalog"

    q.page["meta"] = ui.meta_card(
        box="",
        title="Patient and Employee Healthcare Safety Event Classifier",
        theme="h2o-dark",
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                max_width="1500px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "content",
                        size="1",
                        direction=ui.ZoneDirection.ROW,
                        zones=[
                            ui.zone("navigation", size="20%"),
                            ui.zone("main"),
                        ],
                    ),
                    ui.zone(name="footer"),
                ],
            )
        ],
    )

    commands = [
        ui.command(name='edit_catalog_cmd', label='Edit', icon='QueryList'),
    ]

    # If a dataset has already been uploaded, lets show it on this page
    header = ui.text(" ")
    table = ui.text(" ")
    print(f"prompt_catalog in nav catalog: {q.client.prompt_catalog}")
    if q.client.prompt_catalog is not None:
        print(q.client.prompt_catalog.head())
        #print(f" loc test: {q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].loc[1, 'Prompt_Type']}")

        header = ui.text_l("Prompt Catalog")
        header_subtitle = ui.text("Create new prompts - edit and save existing prompts")
        table = ui.table(
            name="prompt_table",
            columns=[
                ui.table_column(col, col.replace("_", " "), cell_overflow='tooltip', link=True, searchable=True,
                                sortable=True) if col == 'Prompt_ID'
                else ui.table_column(col, col.replace("_", " "),  sortable=True, cell_overflow='tooltip')
                for col in
                q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].columns
            ] + [ui.table_column(name='actions', label='Actions', cell_type=ui.menu_table_cell_type(name='commands', commands=commands))],
            rows=[
                ui.table_row(
                    str(i),
                    [
                        str(q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].loc[i, col])
                        for col in q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']].columns
                    ],
                )
                for i in range(len(q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']]))
            ],
            resettable=True,
            downloadable=True,
            pagination=ui.table_pagination(total_rows=len(q.client.prompt_catalog[['Prompt_ID', 'Prompt_Type', 'Prompt_Text', 'Default']]), rows_per_page=5),
        )

    q.page["catalog"] = ui.form_card(
        box="main",
        items=[header,
               header_subtitle,
               table,
               ],
    )
    q.client.cards.append("catalog")








def email_sent(q: Q):
    clear_cards(q)
    q.page["email_sent"] = ui.form_card(
        box="main", items=[ui.text("Email has been sent to safety_dept@med_center.org!")]
    )
    q.client.cards.append("email_sent")

def no_data(q: Q):
    q.page["no_data"] = ui.form_card(
        box="main", items=[ui.text("Please upload a dataset!")]
    )
    q.client.cards.append("no_data")


def no_config(q: Q):
    q.page["no_config"] = ui.form_card(
        box="main", items=[ui.text("Please configure chat and LLM model!")]
    )
    q.client.cards.append("no_config")


def clear_cards(q: Q):
    # Remove temporal cards from the page
    for card in q.client.cards:
        del q.page[card]

    q.client.cards = []

