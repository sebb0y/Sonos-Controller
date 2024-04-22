import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Scale
import soco

class LoginScreen:
    def __init__(self, root, credentials_file):
        self.root = root
        self.root.title("Login")
        self.root.geometry("400x170")
        self.root.resizable(width=False, height=False)

        self.credentials_file = credentials_file

        self.label_username = ttk.Label(root, text="Username:")
        self.label_username.pack(pady=5)
        self.entry_username = ttk.Entry(root)
        self.entry_username.pack(pady=5)

        self.label_password = ttk.Label(root, text="Password:")
        self.label_password.pack(pady=5)
        self.entry_password = ttk.Entry(root, show="*")
        self.entry_password.pack(pady=5)

        self.button_login = ttk.Button(root, text="Login", command=self.login)
        self.button_login.pack(pady=5)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Check if username and password are correct
        if self.check_credentials(username, password):
            self.root.destroy()  # Close the login window
            sonos_controller = SonosControllerForm()  # Initialize the main app
            sonos_controller.run()  # Run the main app
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def check_credentials(self, username, password):
        try:
            with open(self.credentials_file, "r") as file:
                for line in file:
                    stored_username, stored_password = line.strip().split(":")
                    if username == stored_username and password == stored_password:
                        return True
        except FileNotFoundError:
            messagebox.showerror("Error", "Credentials file not found")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False


class SonosControllerForm:
    def __init__(self):
        # Setting up the GUI form
        self.root = tk.Tk()
        self.root.title("Sonos Controller")
        self.root.geometry("750x450")
        self.root.resizable(width=True, height=False)

        # Set a theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Creating a label to display the current song
        self.current_song_label = ttk.Label(self.root, text="Current Song: ")
        self.current_song_label.pack(pady=5)

        # Creating a label to display the artist
        self.artist_label = ttk.Label(self.root, text="Artist: ")
        self.artist_label.pack(pady=5)

        self.play_button = ttk.Button(self.root, text="Play", command=lambda: (self.play(), self.update_current_song(), self.get_artist(), self.update_ip_address()))
        self.play_button.pack(pady=5)

        self.pause_button = ttk.Button(self.root, text="Pause", command=self.pause,)
        self.pause_button.pack(pady=5)

        # Creating a drop-down menu to display available speakers
        self.speakers_var = tk.StringVar(self.root)
        self.speakers_var.set("Select Speaker")
        self.speakers_menu = ttk.OptionMenu(self.root, self.speakers_var, "Select Speaker")
        self.speakers_menu.pack(pady=5)

        # Volume control
        self.volume_label = ttk.Label(self.root, text="Volume:")
        self.volume_label.pack(pady=5)
        self.volume_scale = Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, command=lambda volume: (self.update_volume(volume), self.update_volume_bar()))
        self.volume_scale.pack(pady=5)

        # Button to update the current song
        self.update_song_button = ttk.Button(self.root, text="Update Current Song", command=self.update_current_song)
        self.update_song_button.pack(pady=5)

        # Button to get the artist of the song
        self.get_artist_button = ttk.Button(self.root, text="Get Artist", command=self.get_artist)
        self.get_artist_button.pack(pady=5)

        # Button to search for Sonos speakers
        self.search_speakers_button = ttk.Button(self.root, text="Search for Sonos System", command=self.search_for_sonos_system)
        self.search_speakers_button.pack(pady=5)
        
        self.label = ttk.Label(self.root, text="Made By Sebb0y")
        self.label.pack()
        

        # Placeholder for discovered Sonos speakers
        self.sonos_speakers = []

        # Bind the update_volume_bar function to the dropdown menu
        self.speakers_var.trace_add("write", self.update_on_speaker_select)

    def search_for_sonos_system(self):
        try:
            self.sonos_speakers = soco.discover()
        except Exception as e:
            messagebox.showerror("Error", f"Error discovering Sonos speakers: {str(e)}")
            return

        if not self.sonos_speakers:
            messagebox.showerror("Error", "No Sonos system found on the network.\nCheck your Internet Connection or Check your Sonos System")
            return

        # Update the speakers menu with the discovered speakers
        self.update_speakers_menu()
        self.search_speakers_button.config(text="System Found")
        

    def update_speakers_menu(self):
        speaker_names = self.get_speaker_names()
        menu = self.speakers_menu["menu"]
        menu.delete(0, "end")

        for name in speaker_names:
            menu.add_command(label=name, command=lambda value=name: self.speakers_var.set(value))

    def get_speaker_names(self):

        return [speaker.player_name for speaker in self.sonos_speakers]

    def update_current_song(self, *_):
        selected_speaker_name = self.speakers_var.get()
        if selected_speaker_name == "Select Speaker":
            messagebox.showerror("Error", "Please Select a Sonos Speaker!")
            return

        for speaker in self.sonos_speakers:
            if speaker.player_name == selected_speaker_name:
                self.current_song = speaker.get_current_track_info().get("title", "No Song Playing")
                self.current_song_label.config(text=f"Current Song: {self.current_song}")
                break

    def get_artist(self, *_):
        selected_speaker_name = self.speakers_var.get()
        if selected_speaker_name == "Select Speaker":
            messagebox.showerror("Error", "Please Select a Sonos Speaker!")
            return

        for speaker in self.sonos_speakers:
            if speaker.player_name == selected_speaker_name:
                current_track_info = speaker.get_current_track_info()
                artist = current_track_info.get("artist", "Unknown Artist")
                self.artist_label.config(text=f"Artist: {artist}")
                break

    def update_volume(self, volume):
        """
        Function to update the volume of the selected Sonos speaker.
        """

        selected_speaker_name = self.speakers_var.get()
        if selected_speaker_name == "Select Speaker":
            messagebox.showerror("Error", "Please Select a Sonos Speaker!")
            return

        for speaker in self.sonos_speakers:
            if speaker.player_name == selected_speaker_name:
                speaker.volume = int(volume)
                break
    
    def play(self):
        
        selected_speaker_name = self.speakers_var.get()
        if selected_speaker_name == "Select Speaker":
            messagebox.showerror("Error", "Please Select a Sonos Speaker!")
            return

        for speaker in self.sonos_speakers:
            if speaker.player_name == selected_speaker_name:
                try:
                    speaker.play()
                except Exception as e:
                    print("Error playing: ", e)
                    break    
    def pause(self):
        selected_speaker_name = self.speakers_var.get()
        if selected_speaker_name == "Select Speaker":
            messagebox.showerror("Error", "Please Select a Sonos Speaker!")
            return

        for speaker in self.sonos_speakers:
            if speaker.player_name == selected_speaker_name:
                speaker.pause()
                self.current_song_label.config(text=f"Playback is Paused!")
                self.artist_label.config(text="No Playback!")

    def update_volume_bar(self):
        """
        Function to update the volume bar based on the selected speaker's volume.
        """

        selected_speaker_name = self.speakers_var.get()
        if selected_speaker_name == "Select Speaker":
            return

        for speaker in self.sonos_speakers:
            if speaker.player_name == selected_speaker_name:
                self.volume_scale.set(speaker.volume)
                break

    def update_on_speaker_select(self, *_):
        self.update_current_song()
        self.get_artist()
        self.update_volume_bar()
        self.update_ip_address()

    def update_ip_address(self):
        selected_speaker_name = self.speakers_var.get()
        if selected_speaker_name == "Select Speaker":
            return

        for speaker in self.sonos_speakers:
            if speaker.player_name == selected_speaker_name:
                print(f"Ip: {speaker.ip_address}")
                break
    def update_system_name(self):
        selected_speaker_name = self.speakers_var.get()
        if selected_speaker_name == "Select Speaker":
            self.system_name_label.config(text="System Name: ")
            return

        for speaker in self.sonos_speakers:
            if speaker.player_name == selected_speaker_name:
                self.system_name_label.config(text=f"System Name: {speaker.player_name}")
                break

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    login_window = tk.Tk()
    login_screen = LoginScreen(login_window, "credentials.txt")
    login_window.mainloop()