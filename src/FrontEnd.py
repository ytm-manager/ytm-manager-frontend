#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid as uuid
from flet import (
    AppBar,
    Page,
    View,
    Container,
    TextField,
    FilePicker,
    Icon,
    PopupMenuButton,
    PopupMenuItem,
    FilePickerResultEvent,
    FilePickerUploadEvent,
    FilePickerUploadFile,
    ProgressRing,
    Ref,
    Column,
    Row,
    alignment,
    margin,
    icons,
    animation,
    transform,
    ButtonStyle,
    TextStyle,
    MaterialState,
    Image,
    RoundedRectangleBorder,
    app,
    AppView
)
import requests
from typing import Dict
from time import sleep

from flet_constructors import *


def make_post_request(url, data):
    """
    Make a POST request to the specified URL with JSON data.

    Args:
        url (str): The URL to send the POST request to.
        data (dict): The JSON data to include in the request body.

    Returns:
        dict or None: The JSON response if the request is successful, None otherwise.
    """
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors (non-2xx status codes)
        return response  # Return response data in JSON format
    except requests.exceptions.RequestException as e:
        print("POST request failed:", e)
        return None


class FrontEnd:
    def __init__(self, page: Page, host_address, host_port, self_host_address, self_host_port):
        self.txt_url: TextField = None
        self.page = page
        self.page.title = "ytm-manager"

        # Configure the theme of the page
        # self.page.theme = theme.Theme(color_scheme_seed="green")
        self.page.theme_mode = "light"

        # Define route buttons
        # Audio URL PopupMenuItem
        self.audio_url_icon_button = create_icon_button(
            lambda _: self.page.go("/audio"),
            "Audio URL",
            icons.AUDIOTRACK,
            icons.AUDIOTRACK_OUTLINED,
            colors.GREY,
            colors.RED
        )

        # Playlist URL PopupMenuItem
        self.playlist_url_icon_button = create_icon_button(
            lambda _: self.page.go("/playlist"),
            "Playlist URL",
            icons.WEBHOOK,  # Replace with the appropriate icon for Playlist URL
            icons.WEBHOOK_OUTLINED,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Audio Upload PopupMenuItem
        self.audio_upload_icon_button = create_icon_button(
            lambda _: self.page.go("/audio/upload"),
            "Audio Upload",
            icons.AUDIO_FILE,
            icons.AUDIO_FILE_OUTLINED,
            colors.GREY,
            colors.RED
        )

        # Playlist Upload PopupMenuItem
        self.playlist_upload_icon_button = create_icon_button(
            lambda _: self.page.go("/playlist/upload"),
            "Playlist Upload",
            icons.LIST,  # Replace with the appropriate icon for Playlist Upload
            icons.LIST_OUTLINED,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Audio Upload 2 PopupMenuItem
        self.audio_upload_2_icon_button = create_icon_button(
            lambda _: self.page.go("/audio/download"),
            "Download Audio",
            icons.DOWNLOAD,  # Replace with the appropriate icon for Audio Upload 2
            icons.DOWNLOAD_DONE_OUTLINED,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Playlist Upload 2 PopupMenuItem
        self.playlist_upload_2_icon_button = create_icon_button(
            lambda _: self.page.go("/playlist/download"),
            "Download Playlist",
            icons.DOWNLOADING,  # Replace with the appropriate icon for Playlist Upload 2
            icons.DOWNLOAD_FOR_OFFLINE,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Define event handlers
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        # Initialize properties
        self.route_change()

        self.host_address = host_address
        self.host_port = host_port

        self.self_host_address = self_host_address
        self.self_host_port = self_host_port

        self.prog_bars: Dict[str, ProgressRing] = {}
        self.files = Ref[Column]()
        self.total_files_to_upload = 0
        self.successfully_uploaded_files = 0
        self.upload_button = Ref[ElevatedButton]()

        self.dialog = Ref[AlertDialog]()

        # Initialize the file picker
        self.file_picker = FilePicker(on_result=self.file_picker_result,
                                      on_upload=self.on_upload_progress)
        self.page.overlay.append(self.file_picker)

    def toggle_dark_mode(self, e):
        # Toggle between light and dark themes
        self.page.theme_mode = "light" if self.page.theme_mode == "dark" else "dark"
        self.page.update()

    def create_menu(self):
        """
        Create the main menu bar (AppBar).

        Returns:
            AppBar: The main menu bar.
        """

        # dark_mode_switch = create_switch("Dark Mode", self.toggle_dark_mode)

        return AppBar(
            leading=Icon(icons.DOWNLOAD_FOR_OFFLINE),
            leading_width=40,
            title=Text("ytm-offline"),
            center_title=False,
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                self.audio_url_icon_button,
                self.playlist_url_icon_button,
                self.audio_upload_icon_button,
                self.playlist_upload_icon_button,
                self.audio_upload_2_icon_button,
                self.playlist_upload_2_icon_button,
                PopupMenuButton(
                    items=[
                        PopupMenuItem(
                            text="Dark Mode",
                            icon=icons.DARK_MODE,
                            on_click=self.toggle_dark_mode
                        ),
                        PopupMenuButton(),
                        PopupMenuItem(
                            text="Register",
                            icon=icons.SUPERVISED_USER_CIRCLE,
                            on_click=lambda _: self.page.go("/register")
                        ),
                        PopupMenuButton(),
                        PopupMenuItem(
                            text="Log In",
                            icon=icons.ACCESSIBILITY_NEW,
                            on_click=lambda _: self.page.go("/login")
                        )
                    ],
                )
            ]
        )

    def create_page_body(self):
        """
        Create the main content of the page.

        Returns:
            Text: A Text component representing the main content.
        """
        self.page.vertical_alignment="center"
        self.page.horizontal_alignment="center"

        isLogin = Text("Login",
                       weight="bold",
                       color="white",
                       size=20,

                       offset=transform.Offset(0,0),
                       animate_offset=animation.Animation(duration=300)
                       )

        # Logic register button
        def ganti(e):
            # Animation of the ctx container

            ctx.bgcolor = "blue" if isLogin.value == "Login" else "red"
            ctx.height = 800 if isLogin.value == "Login" else 150
            ctx.width = 300 if isLogin.value == "Login" else 200
            ctx.border_radius = 0 if isLogin.value == "Login" else 100

            # isLogin animation
            isLogin.value = "Register" if isLogin.value == "Login" else "Login"
            isLogin.offset = transform.Offset(5, 0) if isLogin.value == "Login" else transform.Offset(0, 0)

            # register animation button hide and show
            register_btn.value = "Register" if isLogin.value == "Login" else "Login"
            register_btn.offset = transform.Offset(0, 0) if isLogin.value == "Login" else transform.Offset(5, 0)

            # Show hide you register form here
            txt_box_register.visible = True if isLogin.value == "Register" else False

            self.page.update()

        txt_box_register = Container(
            content=Column([
                TextField(label="Username",
                          border_color="white",
                          color="white",
                          ),
                TextField(label="Password",
                          border_color="white",
                          color="white",
                          ),
                # Login Button
                ElevatedButton(
                    width=self.page.window_width,
                    on_click=ganti
                )
            ])
        )

        # Set Register is hidden
        txt_box_register.visible = False

        # Register button
        register_btn = ElevatedButton("Register",
                                      on_click=ganti,
                                      offset=transform.Offset(0,0),
                                      animate_offset=animation.Animation(duration=300)
        )

        ctx = Container(
            bgcolor="red",
            alignment=alignment.center,
            border_radius=100,
            padding=20,
            width=1000,
            height=800,
            animate=animation.Animation(duration=300, curve="easyInOut"),
            content=Column(
                controls=[
                    Container(
                        width=300,
                        margin=margin.only(left=170, right=10, top=10),
                        content=TextButton(
                            "Create Account",
                            style=ButtonStyle(
                                color="#000000"
                            )
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=110, right=10, top=25),
                        content=Text(
                            "Login",
                            size=30,
                            color="#000000",
                            weight="w700"
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=20),
                        alignment=alignment.center,
                        content=Text(
                            "Please enter your information below in order to log in to your account",
                            size=14,
                            color="#000000",
                            text_align="center"
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=35),
                        content=Column(
                            controls=[
                                Text(
                                    "Username",
                                    size=14,
                                    color="#000000"
                                ),
                                TextField(
                                    text_style=TextStyle(
                                        color="#000000"
                                    ),
                                    border_radius=15,
                                    border_color=colors.BLACK,
                                    focused_border_color=colors.WHITE70,
                                )
                            ]
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=5),
                        content=Column(
                            controls=[
                                Text(
                                    "Password",
                                    size=14,
                                    color="#000000"
                                ),
                                TextField(
                                    text_style=TextStyle(
                                        color="#000000"
                                    ),
                                    password=True,
                                    can_reveal_password=True,
                                    border_radius=15,
                                    border_color=colors.BLACK,
                                    focused_border_color=colors.WHITE70,
                                )
                            ]
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=120),
                        content=TextButton(
                            "Forgot Password?",
                            style=ButtonStyle(
                                color="#000000",
                            )
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=10),
                        content=ElevatedButton(
                            "Login",
                            width=300,
                            height=55,
                            style=ButtonStyle(
                                color="#ffffff",
                                bgcolor=colors.ORANGE_700,
                                shape={
                                    MaterialState.FOCUSED: RoundedRectangleBorder(radius=5),
                                    MaterialState.HOVERED: RoundedRectangleBorder(radius=5),
                                },
                                padding=20,
                            )
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=15),
                        content=Text(
                            "Or use social media account for login",
                            size=14,
                            text_align="center",
                            color="#000000",
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=15),
                        content=Row(
                            controls=[
                                Container(
                                    Image(
                                        r"assets\facebook.png",
                                        width=48,
                                    ),
                                    margin=margin.only(right=10),
                                    # you can use this as button using on_click
                                    on_click = lambda _: print("facebook")  # respected function here
                                ),
                                Container(
                                    Image(
                                        r"assets\google.png",
                                        width=48,
                                    ),
                                    margin=margin.only(right=10),
                                    # you can use this as button using on_click
                                    on_click = lambda _: print("google")  # respected function here
                                ),
                                Container(
                                    Image(
                                        r"assets\gmail.png",
                                        width=48,
                                    ),
                                    margin=margin.only(right=10),
                                    # you can use this as button using on_click
                                    on_click=lambda _: print("gmail")  # respected function here
                                ),
                            ],
                            alignment=MainAxisAlignment.CENTER,
                        )
                    )

                ]
            )
        )
        return ctx

    def create_main_view(self):
        """
        Create the main view that includes the menu bar and page body.

        Returns:
            View: The main view.
        """
        return View(
            "/",
            [
                self.create_menu(),
                self.create_page_body()
            ],
        )

    def file_picker_result(self, e: FilePickerResultEvent):
        """
        Handle file picker results.

        Args:
            e (FilePickerResultEvent): The event object containing file picker results.
        """
        self.upload_button.current.disabled = True if e.files is None else False
        self.prog_bars.clear()
        self.files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ProgressRing(
                    value=0,
                    bgcolor="#eeeeee",
                    width=20,
                    height=20
                )
                self.prog_bars[f.name] = prog
                self.files.current.controls.append(Row([prog, Text(f.name)]))
        self.page.update()

    def on_upload_progress(self, e: FilePickerUploadEvent):
        """
        Handle file upload progress.

        Args:
            e (FilePickerUploadEvent): The event object containing file upload progress information.
        """
        self.prog_bars[e.file_name].value = e.progress
        self.prog_bars[e.file_name].update()

        if e.progress == 1:  # Check if the upload progress is 100%
            self.increment_uploaded_files_count()  # Call the function to increment the count

    def show_success_dialog(self):
        if self.total_files_to_upload == 1 and self.successfully_uploaded_files == self.total_files_to_upload:
            self.show_simple_alert_dialog("File Uploaded", "File has been uploaded!", False)
            # self.show_modal_alert_dialog("File Uploaded", "File has been uploaded!", lambda _: self.close_dlg(), lambda _: self.close_dlg())
        elif self.total_files_to_upload > 1 and self.successfully_uploaded_files == self.total_files_to_upload:
            self.show_simple_alert_dialog("Files Uploaded",
                                   f"All {self.total_files_to_upload} files have been uploaded!",
                                   False)

    def show_error_dialog(self, title_text, error_message):
        """
        Show an error dialog with a title and error message.

        Args:
            title_text (str): The title of the error dialog.
            error_message (str): The error message to display.
        """
        # Create an error alert dialog with the given title and error message
        error_dialog = create_simple_alert_dialog(title_text, error_message)

        # Show the error dialog
        self.open_dlg(error_dialog)

    def increment_uploaded_files_count(self):
        self.successfully_uploaded_files += 1
        self.show_success_dialog()

    def upload_files(self, e):
        """
        Upload selected files when the "Upload" button is clicked.

        Args:
            e: The event object (not used).
        """
        self.total_files_to_upload = 0
        self.successfully_uploaded_files = 0
        upload_list = []

        if self.file_picker.result is not None and self.file_picker.result.files is not None:
            self.total_files_to_upload = len(self.file_picker.result.files)  # Update the total count of files
            for f in self.file_picker.result.files:
                upload_list.append(
                    FilePickerUploadFile(
                        f.name,
                        upload_url=self.page.get_upload_url(f.name, 600),
                    )
                )
            self.file_picker.upload(upload_list)

    def create_custom_upload_file_view(self, view_path, view_name):
        """
        Create a view for uploading files.

        Args:
            view_path (str): The route path for the upload view.
            view_name (str): The name of the upload view.

        Returns:
            View: The upload file view.
        """
        return View(
            view_path,
            [
                AppBar(
                    title=Text(view_name),
                    bgcolor=colors.SURFACE_VARIANT
                ),
                Text("This is the " + view_name + " Page"),
                create_button(
                    "Select files...",
                    lambda _: self.file_picker.pick_files(allow_multiple=True),
                    icon=icons.FOLDER_OPEN
                ),
                Column(ref=self.files),
                create_button("Upload", self.upload_files, icons.UPLOAD, self.upload_button, True)
            ],
        )

    def open_dlg(self, dlg):
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def close_dlg(self):
        dlg = self.page.dialog
        dlg.open = False
        self.page.update()

    def show_simple_alert_dialog(self, title_text, content_text, is_auto_closed=True, delay=2):
        # Create an alert dialog with the given title and content
        alert_dialog = create_simple_alert_dialog(title_text, content_text)

        # Show the dialog
        self.open_dlg(alert_dialog)

        # Close the dialog and print the message when all files are uploaded
        if is_auto_closed:
            sleep(delay)
            self.close_dlg()

    def show_modal_alert_dialog(self, title_text, content_text, yes_func, no_func):
        # Create an alert dialog with the given title and content
        alert_dialog = create_modal_alert_dialog(title_text, content_text, yes_func, no_func)

        # Show the dialog
        self.open_dlg(alert_dialog)

    def route_change(self, e=None):
        """
        Handle route changes and update views accordingly.

        Args:
            e: The event object (not used).
        """
        self.page.views.clear()
        self.page.views.append(self.create_main_view())

        if self.page.route == "/audio":
            self.txt_url = TextField(label="Enter song URL")
            print("INITIALIZING TEXT URL WITH THE TEXT", self.txt_url.value)
            self.page.views.append(
                create_custom_view(self.txt_url, "/audio", "Audio URL", self.submit_audio)
            )
            print("View is created.")

        if self.page.route == "/playlist":
            self.txt_url = TextField(label="Enter playlist URL")
            self.page.views.append(
                create_custom_view(self.txt_url, "/playlist", "Playlist URL", self.submit_playlist)
            )

        if self.page.route == "/audio/upload":
            self.page.views.append(
                self.create_custom_upload_file_view("/audio/upload", "Upload .mp3 audio")
            )

        if self.page.route == "/playlist/upload":
            self.page.views.append(
                self.create_custom_upload_file_view("/playlist/upload", "Upload .zip playlist")
            )

        if self.page.route == "/audio/download":
            self.txt_url = TextField(label="Enter playlist URL")
            self.page.views.append(
                self.create_custom_view(self.txt_url, "/audio/download", "Download Audio", self.download_audio)
            )

        if self.page.route == "/playlist/download":
            self.txt_url = TextField(label="Enter playlist URL")
            self.page.views.append(
                self.create_custom_view(self.txt_url, "/playlist/download", "Download Playlist", self.download_playlist)
            )

        if self.page.route == "/login":
            print("login")
            self.txt_url = TextField(label="Log In")
            self.page.views.append(
                create_custom_view(self.txt_url, "/login", "Log In", self.submit_playlist)
            )

        if self.page.route == "/register":
            print("register")
            self.txt_url = TextField(label="Register")
            self.page.views.append(
                create_custom_view(self.txt_url, "/register", "Register", self.submit_playlist)
            )

        self.page.update()

    def view_pop(self, e=None):
        """
        Handle view popping (removing the top view).

        Args:
            e: The event object (not used).
        """
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def submit_audio(self, txt_url, e=None):
        """
        Handle audio submission when the "Submit" button is clicked.

        Args:
            txt_url (str): The entered audio URL.
            e: The event object (not used).
        """
        self.make_audio_upload_request(self.txt_url.value)

    def submit_playlist(self, txt_url, e=None):
        """
        Handle playlist submission when the "Submit" button is clicked.

        Args:
            txt_url (str): The entered playlist URL.
            e: The event object (not used).
        """
        print("HERE WE SUBMIT THE PLAYLIST")
        self.make_playlist_upload_request(self.txt_url.value)
        print("DONE")

    def download_audio(self, empty):
        """


        :return:
        """
        self.make_download_audio_request(self.txt_url.value)

    def download_playlist(self, empty):
        self.make_download_playlist_request(self.txt_url.value)

    def make_audio_upload_request(self, link):
        """
        Make a POST request to upload an audio file.

        Args:make_audio_upload_request
            link (str): The audio URL to upload.
        """
        print("MAKE AUDIO UPLOAD REQUEST")
        request_data = {"audio_url": link}
        print("the request data:\n", request_data)
        response = make_post_request('http://' + self.host_address + ':' + self.host_port + '/api/global/uploadAudio', request_data)
        print("RESPONSE:\t", response)
        if response is None:
            # If the request failed, show an error dialog
            self.show_error_dialog("Error", "Failed to upload audio.")
        elif response.status_code == 200:
            #  TODO: Success dialog with a custom message
            print(200)
            self.show_simple_alert_dialog("File uploaded!", "Audio uploaded successfully.", True, 10)
        elif response.status_code == 401:
            # If the request failed, show an error dialog
            self.show_error_dialog("Unauthorized", "The audio was not uploaded because your YouTube Music token was not authorized to do the upload."
                                                   "Refresh your token and try again.")
        else:
            self.show_error_dialog("Error", "There server responded:\t" + str(response.status_code))

    def make_playlist_upload_request(self, link):
        """
        Make a POST request to upload a playlist.

        Args:
            link (str): The playlist URL to upload (not implemented).
        """
        print("MAKE AUDIO UPLOAD REQUEST")
        request_data = {"playlist_url": link}
        print("the request data:\n", request_data)
        response = make_post_request('http://' + self.host_address + ':' + self.host_port + '/api/global/uploadPlaylist',
                                     request_data)
        print("RESPONSE:\t", response)
        if response is None:
            # If the request failed, show an error dialog
            self.show_error_dialog("Error", "Failed to upload playlist.")
        elif response.status_code == 200:
            #  TODO: Success dialog with a custom message
            print(200)
            self.show_simple_alert_dialog("Playlist uploaded!", "Success.", True, 10)
        elif response.status_code == 401:
            # If the request failed, show an error dialog
            self.show_error_dialog("Unauthorized",
                                   "The playlist was not uploaded because your YouTube Music token was not authorized to do the upload."
                                   "Refresh your token and try again.")
        else:
            self.show_error_dialog("Error", "There server responded:\t" + str(response.status_code))

    def make_download_audio_request(self, link):
        """
        Make a POST request to download an audio.

        Args:
            link (str): The playlist URL to upload (not implemented).
        """
        print("MAKE AUDIO DOWNLOAD REQUEST")
        request_data = {"audio_url": link}
        print("the request data:\n", request_data)
        response = make_post_request(
            'http://' + self.host_address + ':' + self.host_port + '/api/global/downloadAudio',
            request_data)
        print("RESPONSE:\t", response)
        if response is None:
            # If the request failed, show an error dialog
            self.show_error_dialog("Error", "Failed to download audio.")
        elif response.status_code == 200:
            #  TODO: Success dialog with a custom message
            print(200)
            self.show_simple_alert_dialog("Audio downloaded!", "Success.", True, 10)
            data = response.content
            file_name = uuid.uuid4()
            with open("assets/uploads/" + str(file_name), 'wb') as s:
                s.write(data)

            url = "http://" + self.self_host_address + ":" +  self.self_host_port + "/assets/uploads/" + str(file_name)
            self.page.launch_url(url)
        elif response.status_code == 401:
            # If the request failed, show an error dialog
            self.show_error_dialog("Unauthorized",
                                   "The audio was not downloaded")
        else:
            self.show_error_dialog("Error", "There server responded:\t" + str(response.status_code))

    def make_download_playlist_request(self, link):
        """
        Make a POST request to download a playlist.

        Args:
            link (str): The playlist URL to upload (not implemented).
        """
        print("MAKE PLAYLIST DOWNLOAD REQUEST")
        request_data = {"audio_url": link}
        print("the request data:\n", request_data)
        response = make_post_request(
            'http://' + self.host_address + ':' + self.host_port + '/api/global/downloadPlaylist',
            request_data)
        print("RESPONSE:\t", response)
        if response is None:
            # If the request failed, show an error dialog
            self.show_error_dialog("Error", "Failed to download playlist.")
        elif response.status_code == 200:
            #  TODO: Success dialog with a custom message
            print(200)
            self.show_simple_alert_dialog("Playlist downloaded!", "Success.", True, 10)
            data = response.content
            file_name = uuid.uuid4()
            with open("assets/uploads/" + str(file_name), 'wb') as s:
                s.write(data)

            url = "http://" + self.self_host_address + ":" +  self.self_host_port + "/assets/uploads/" + str(file_name)
            self.page.launch_url(url)
        elif response.status_code == 401:
            # If the request failed, show an error dialog
            self.show_error_dialog("Unauthorized",
                                   "The playlist was not downloaded")
        else:
            self.show_error_dialog("Error", "There server responded:\t" + str(response.status_code))


def main(page: Page):
    host_address = os.environ.get("BACKEND_HOST")
    host_port = os.environ.get("BACKEND_PORT")

    self_host_address = os.environ.get("FRONTEND_HOST")
    self_host_port = os.environ.get("FRONTEND_PORT")

    if host_address is None:
        host_address = "127.0.0.1"

    if host_port is None:
        host_port = "5000"

    if self_host_address is None:
        self_host_address = "127.0.0.1"

    if self_host_port is None:
        self_host_port = "5010"


    frontend = FrontEnd(page, host_address, host_port, self_host_address, self_host_port)
    page.go(page.route)


if __name__ == '__main__':
    app(main, view=AppView.WEB_BROWSER, assets_dir="assets", port=5010, host="0.0.0.0", upload_dir="assets/uploads")
