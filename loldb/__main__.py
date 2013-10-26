from .main import main

mac_path = "/Applications/League of Legends.app/Contents/LOL"
mac_path2 = "/LOLAPP/Contents/LOL"
win_path = "C:/Riot Games/League of Legends"
main(
    corrections_path='corrections.json',
    base_path=mac_path2,
    output_name='league',
    archives_path='archive',
)
