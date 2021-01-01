import pygame

from pang_client.pang_client_main import game_loop, PlayMode

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("PANG")
    game_loop(play_mode=PlayMode.NEW, online=False, replay_file="data/recording.json")
    pygame.quit()
