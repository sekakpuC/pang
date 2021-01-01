import pygame

from main import game_loop, PlayMode

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("PANG")
    game_loop(play_mode=PlayMode.REPLAY,
              online=False,
              replay_file="data/recording.json",
              center_msg="Enjoy your last play!")
    pygame.quit()
