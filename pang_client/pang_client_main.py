import datetime
import enum
import json
import socket
import sys
from random import randint

import pygame

from pang_client.pang_client_opts import parse_pang_client_ini_options, parse_pang_client_cli_options, print_options


class PlayMode(enum.Enum):
    NEW = 'new',
    REPLAY = 'replay'


GAME_RESULT_REASON_QUIT = "Quit"
GAME_RESULT_REASON_ESCAPE_KEY = "Quit by ESC"
GAME_RESULT_REASON_SUCCESS = "Success"
GAME_RESULT_REASON_TIMEOVER = "Time Over"
GAME_RESULT_REASON_DIED = "Died"
GAME_RESULT_REASON_NO_MORE_REPLAY_LOG = "No more replay log"
GAME_RESULT_REASON_GAME_OVER = "Game OVer"


def save_snapshot(gd: dict, snapshot: dict):
    output_fd = gd['output_fd']
    json_string = json.dumps(snapshot)
    output_fd.write(json_string + "\n")


def build_snapshot_obj(state: dict, events: dict):
    snapshot = {"state": state, "events": events}
    return snapshot


def build_state_obj(ball_dict: dict, player_dict: dict, weapons_dict: dict):
    state = {"balls": ball_dict, "players": player_dict, "weapons": weapons_dict}
    return state


def get_events(mode: PlayMode, replay_events: list):
    if mode == PlayMode.REPLAY:
        result: list = replay_events
        for e in pygame.event.get():
            if e:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        a = {"type": e.type, "key": e.key}
                        result.append(a)
                elif e.type == pygame.QUIT:
                    a = {"type": e.type}
                    result.append(a)
        return result
    else:
        result = []
        for e in pygame.event.get():
            a = {}
            if e.type:
                a["type"] = e.type
                if hasattr(e, "key"):
                    a["key"] = e.key
                result.append(a)
        return result


def read_snapshot_obj_from_file(input_fd):
    json_str = input_fd.readline()
    try:
        snapshot = json.loads(json_str)
        return snapshot
    except:
        print(f"DEBUG reached the end of replay data [{json_str}]")
        return None


def send_snapshot_to_server(sock: socket, data_dict: dict):
    data_dict["type"] = "snapshot"
    data_str = json.dumps(data_dict)
    data_byte = str.encode(data_str)
    data_byte_len_int = len(data_byte)
    data_byte_len_str = "{:<10}".format(data_byte_len_int)
    data_byte_len_byte = str.encode(data_byte_len_str)
    n_written = sock.send(data_byte_len_byte)
    if n_written != 10:
        print(f"WARN at line 88, {n_written} written. tried to write 10 bytes")
    n_written = sock.send(data_byte)
    if n_written != data_byte_len_int:
        print(f"WARN at line 91, {n_written} written. tried to write {data_byte_len_int}")
    # print(f"DEBUG Sent snapshot data: len {data_byte_len_int} to the server.")


def send_score_to_server(sock: socket, username: str, score: int):
    data_dict = {
        "type": "score",
        "username": username,
        "score": score,
    }
    data_str = json.dumps(data_dict)
    data_byte = str.encode(data_str)
    data_byte_len_int = len(data_byte)
    data_byte_len_str = "{:<10}".format(data_byte_len_int)
    data_byte_len_byte = str.encode(data_byte_len_str)
    n_written = sock.send(data_byte_len_byte)
    if n_written != 10:
        print(f"WARN at line 108, {n_written} written. tried to write 10 bytes")
    n_written = sock.send(data_byte)
    if n_written != data_byte_len_int:
        print(f"WARN at line 111, {n_written} written. tried to write {data_byte_len_int}")
    print(f"DEBUG Sent score data: {username}, {score} to the server.")


def display_press_escape_msg(gd: dict, center_msg: str):
    msg = gd["game_font"].render(center_msg, True, (255, 255, 255))
    msg_rect = msg.get_rect()
    msg_width, msg_height = msg_rect.size
    gd["screen"].blit(msg, (gd["screen_width"] / 2 - msg_width / 2, gd["screen_height"] / 2 - msg_height / 2))


def read_balls_players_weapons_events_from_file(gd: dict):
    input_fd = gd['input_fd']
    old_snapshot = read_snapshot_obj_from_file(input_fd)
    if old_snapshot:
        old_state = old_snapshot["state"]
        balls, players, weapons = old_state["balls"], old_state["players"], old_state["weapons"]
        events = old_snapshot["events"]
        return balls, players, weapons, events
    else:
        print(f"DEBUG no snapshot data.")
        return None


def display_game_result(gd: dict):
    game_result = gd['game_result']
    # print(f"DEBUG game_result: {game_result}")
    msg = gd['game_font'].render(game_result, True, (255, 255, 255))
    msg_rect = msg.get_rect()
    msg_width, msg_height = msg_rect.size
    gd['screen'].blit(msg, (gd['screen_width'] / 2 - msg_width / 2, gd['screen_height'] / 2 - msg_height / 2))
    pygame.display.update()


def init_pang(play_mode: str, online: bool, host: str, port: int):
    gd = dict()
    gd['play_mode'] = play_mode
    gd['online'] = online
    gd['replay_running'] = True
    gd['score'] = 0
    gd['host'] = host
    gd['port'] = port
    gd["screen_width"] = screen_width = 640
    gd["screen_height"] = screen_height = 480
    gd["screen"] = pygame.display.set_mode((screen_width, screen_height))
    gd['background_img'] = pygame.image.load("images/background.png")
    gd['player_img'] = pygame.image.load("images/player.png")
    gd['weapon_img'] = pygame.image.load("images/weapon.png")
    gd['floor_img'] = pygame.image.load("images/floor.png")
    gd['ball_img_list'] = [
        pygame.image.load("images/ball1.png"),
        pygame.image.load("images/ball2.png"),
        pygame.image.load("images/ball3.png"),
        pygame.image.load("images/ball4.png")]
    gd['clock'] = pygame.time.Clock()
    gd['floor_width'], gd['floor_height'] = gd['floor_img'].get_rect().size
    gd['player_width'], gd['player_height'] = gd['player_img'].get_rect().size
    gd['weapon_width'], gd['weapon_height'] = gd['weapon_img'].get_rect().size
    gd['players'] = [create_player_obj(gd)]
    gd['max_weapons'] = 2
    gd['weapons'] = []
    gd['weapon_speed'] = -7
    gd['ball_init_y_speed_list'] = [-14, -13, -12, -11]
    gd['balls'] = [{
        "xpos": 50,
        "ypos": 50,
        "img_idx": 0,
        "to_x": 3,
        "to_y": -6,
        "init_speed_y": gd['ball_init_y_speed_list'][0]
    }]
    gd['weapon_to_remove'] = -1
    gd['ball_to_remove'] = -1
    gd["game_font"] = pygame.font.Font(None, 40)
    gd["total_time"] = 30
    gd['start_ticks'] = pygame.time.get_ticks()
    gd['game_result'] = GAME_RESULT_REASON_GAME_OVER
    return gd


def create_player_obj(gd: dict):
    player = {
        "speed": .6,
        "to_x": 0,
        "xpos": (gd['screen_width'] / 2) - (gd['player_width'] / 2),
        "ypos": gd['screen_height'] - gd['floor_height'] - gd['player_height']
    }
    return player


def draw_timer(gd: dict, remaining_time: int):
    timer = gd['game_font'].render("Time: {}".format(remaining_time), True, (255, 255, 255))
    gd['screen'].blit(timer, (10, 10))


def get_remaining_time_in_secs(gd: dict):
    start_ticks = gd['start_ticks']
    elapsed_time = get_elapsed_time_in_secs(start_ticks)
    remaining_time = int(gd['total_time'] - elapsed_time)
    return remaining_time


def get_elapsed_time_in_secs(start_ticks: int):
    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
    return elapsed_time


def draw_objects(gd: dict):
    screen = gd['screen']
    background_img = gd['background_img']
    weapons = gd['weapons']
    weapon_img = gd['weapon_img']
    floor_img = gd['floor_img']
    player_img = gd['player_img']
    ball_img_list = gd['ball_img_list']
    balls = gd['balls']
    players = gd['players']
    player1 = players[0]

    screen.blit(background_img, (0, 0))
    for weapon_xpos, weapon_ypos in weapons:
        screen.blit(weapon_img, (weapon_xpos, weapon_ypos))
    screen.blit(floor_img, (0, gd['screen_height'] - gd['floor_height']))
    screen.blit(player_img, (player1["xpos"], gd['screen_height'] - gd['floor_height'] - gd['player_height']))
    for ball_idx, ball in enumerate(balls):
        ball_xpos = ball["xpos"]
        ball_ypos = ball["ypos"]
        ball_img_idx = ball["img_idx"]
        screen.blit(ball_img_list[ball_img_idx], (ball_xpos, ball_ypos))


def handle_conflicts(gd: dict):
    balls = gd['balls']
    players = gd['players']

    player_rect = update_player_pos_and_get_player_rect(gd, players)
    running = True
    for ball_idx, ball in enumerate(balls):
        ball_rect = update_ball_pos_and_get_ball_rect(gd, ball)
        if player_rect.colliderect(ball_rect):
            gd['game_result'] = "You died"
            running = False
            break
        for weapon_idx, weapon in enumerate(gd['weapons']):
            weapon_rect = update_weapon_pos_and_get_weapon_rect(gd, weapon)
            if weapon_rect.colliderect(ball_rect):
                increment_score(gd)
                mark_ball_and_weapon_to_be_destroyed(gd, ball_idx, weapon_idx)
                if ball['img_idx'] != 3:
                    split_ball(gd, ball_rect, ball)
                break
        else:
            continue
        break
    destroy_marked_ball(gd)
    destroy_marked_weapon(gd)
    return running


def destroy_marked_weapon(gd: dict):
    weapon_to_remove = gd['weapon_to_remove']
    if weapon_to_remove > -1:
        weapons = gd['weapons']
        del weapons[weapon_to_remove]
        gd['weapon_to_remove'] = -1


def destroy_marked_ball(gd: dict):
    ball_to_remove = gd['ball_to_remove']
    if ball_to_remove > -1:
        balls = gd['balls']
        del balls[ball_to_remove]
        gd['ball_to_remove'] = -1


def update_weapon_pos_and_get_weapon_rect(gd: dict, weapon: tuple):
    weapon_rect = gd['weapon_img'].get_rect()
    weapon_rect.left = weapon[0]
    weapon_rect.top = weapon[1]
    return weapon_rect


def update_ball_pos_and_get_ball_rect(gd: dict, ball: dict):
    ball_img_list = gd['ball_img_list']
    ball_xpos = ball["xpos"]
    ball_ypos = ball["ypos"]
    ball_img_idx = ball["img_idx"]
    ball_rect = ball_img_list[ball_img_idx].get_rect()
    ball_rect.left = ball_xpos
    ball_rect.top = ball_ypos
    return ball_rect


def update_player_pos_and_get_player_rect(gd: dict, players: list):
    player_img = gd['player_img']
    player_rect = player_img.get_rect()
    player1 = players[0]
    player_rect.left = player1["xpos"]
    player_rect.top = player1["ypos"]
    return player_rect


def split_ball(gd: dict, ball_rect: pygame.Rect, ball: dict):
    balls = gd['balls']
    ball_img_list = gd['ball_img_list']
    ball_img_idx = ball['img_idx']
    ball_xpos = ball['xpos']
    ball_ypos = ball['ypos']
    ball_init_y_speed_list = gd['ball_init_y_speed_list']

    ball_width = ball_rect.size[0]
    ball_height = ball_rect.size[1]
    small_ball_rect = ball_img_list[ball_img_idx + 1].get_rect()
    small_ball_width = small_ball_rect.size[0]
    small_ball_height = small_ball_rect.size[1]
    # smaller ball on the right
    balls.append({
        "xpos": ball_xpos + (ball_width / 2) - (small_ball_width / 2),
        "ypos": ball_ypos + (ball_height / 2) - (small_ball_height / 2),
        "img_idx": ball_img_idx + 1,
        "to_x": 3,
        "to_y": -8,
        "init_speed_y": ball_init_y_speed_list[ball_img_idx + 1]
    })
    # smaller ball on the left
    balls.append({
        "xpos": ball_xpos + (ball_width / 2) - (small_ball_width / 2),
        "ypos": ball_ypos + (ball_height / 2) - (small_ball_height / 2),
        "img_idx": ball_img_idx + 1,
        "to_x": -3,
        "to_y": -8,
        "init_speed_y": ball_init_y_speed_list[ball_img_idx + 1]
    })


def mark_ball_and_weapon_to_be_destroyed(gd: dict, ball_idx: int, w_idx: int):
    gd['weapon_to_remove'] = w_idx
    gd['ball_to_remove'] = ball_idx


def increment_score(gd: dict):
    gd['score'] += round((pygame.time.get_ticks() - gd['start_ticks']), 0)


def read_events_and_apply_changes(gd: dict, play_mode: PlayMode, replay_events: dict):
    events = []
    is_quit = False
    is_esc = False
    players = gd['players']
    player1 = players[0]
    for event in get_events(play_mode, replay_events):
        events.append(event)
        event_type = event["type"]
        if event_type == pygame.QUIT:
            is_quit = True
        if event_type == pygame.KEYDOWN:
            if event["key"] == pygame.K_LEFT:
                player1["to_x"] -= player1["speed"]
            elif event["key"] == pygame.K_RIGHT:
                player1["to_x"] += player1["speed"]
            elif event["key"] == pygame.K_SPACE:
                if len(gd['weapons']) < gd['max_weapons']:
                    weapon_xpos = player1["xpos"] + (gd['player_width'] / 2) - (gd['weapon_width'] / 2)
                    weapon_ypos = player1["ypos"]
                    gd['weapons'].append([weapon_xpos, weapon_ypos])
            elif event["key"] == pygame.K_ESCAPE:
                is_esc = True
        if event_type == pygame.KEYUP:
            if event["key"] == pygame.K_LEFT or event["key"] == pygame.K_RIGHT:
                player1["to_x"] = 0
    gd['events'] = events
    return is_quit, is_esc


def update_ball_position(gd: dict):
    balls = gd['balls']
    ball_img_list = gd['ball_img_list']
    screen_width = gd['screen_width']
    screen_height = gd['screen_height']
    floor_height = gd['floor_height']
    for ball_idx, ball_val in enumerate(balls):
        ball_xpos = ball_val["xpos"]
        ball_ypos = ball_val["ypos"]
        ball_img_idx = ball_val["img_idx"]

        ball_width, ball_height = ball_img_list[ball_img_idx].get_rect().size

        if ball_xpos < 0 or ball_xpos > (screen_width - ball_width):
            ball_val["to_x"] *= -1
        if ball_ypos > (screen_height - floor_height - ball_height):
            ball_val["to_y"] = ball_val["init_speed_y"]
        else:
            ball_val["to_y"] += .4

        ball_val["xpos"] += ball_val["to_x"]
        ball_val["ypos"] += ball_val["to_y"]


def update_weapons_position(gd: dict):
    weapons = gd['weapons']
    weapon_speed = gd['weapon_speed']
    for w in weapons:
        w[1] += weapon_speed
    weapons = [[w[0], w[1]] for w in weapons if w[1] > 0]
    return weapons


def random_name_picker():
    names = ['Addison', 'Aubrey', 'Audrey', 'Austin', 'Avery',
             'Bryson', 'Carter', 'Christian', 'Colton', 'Cooper',
             'Easton', 'Eleanor', 'Ella', 'Ellie', 'Evelyn',
             'Everett', 'Everly', 'Grayson', 'Greyson', 'Hailey',
             'Harper', 'Hazel', 'Hudson', 'Hunter', 'Ivy',
             'Jack', 'Jackson', 'James', 'Jameson', 'Jaxon',
             'Julian', 'Kinsley', 'Landon', 'Lillian', 'Lily',
             'Lincoln', 'Lucy', 'Madeline', 'Madison', 'Mason',
             'Miles', 'Parker', 'Peyton', 'Piper', 'Robert',
             'Scarlett', 'Wesley', 'William', 'Willow', 'Wyatt', ]
    return names[randint(0, len(names) - 1)]


def update_player_position(gd: dict, dt: int):
    player1 = gd['players'][0]
    player1["xpos"] += player1["to_x"] * dt
    if player1["xpos"] < 0:
        player1["xpos"] = 0
    elif player1["xpos"] > gd['screen_width'] - gd['player_width']:
        player1["xpos"] = gd['screen_width'] - gd['player_width']


def game_loop(play_mode: PlayMode = None,
              online: bool = False,
              server_host: str = "localhost",
              server_port: int = 2345,
              replay_file: str = "data/recording.json",
              center_msg: str = "",
              display_timer: bool = True):
    # print(f"DEBUG {datetime.datetime.now()} starting game loop")
    gd = init_pang(play_mode, online, server_host, server_port)

    if play_mode == PlayMode.NEW:
        username = random_name_picker()
        print(f"DEBUG Playing game as '{username}'")
        if online:
            gd['sock'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                gd['sock'].connect((gd['host'], gd['port']))
                print(f"DEBUG Connecting to {gd['host']}:{gd['port']}...")
            except:
                print(f"WARN Failed to connect to {gd['host']}:{gd['port']}. Switched to offline mode.")
                online = False

    if play_mode == PlayMode.NEW:
        gd['output_fd'] = open(replay_file, "w")
        print(f"DEBUG Opened output file {replay_file}")
    elif play_mode == PlayMode.REPLAY:
        gd['input_fd'] = open(replay_file, "r")
        print(f"DEBUG Opened input file {replay_file} for replay")
    is_quit_clicked = False
    is_esc_pressed = False
    replay_running = True
    running = True
    while running:
        dt = gd['clock'].tick(60)

        replay_events = None
        if play_mode == PlayMode.NEW:
            balls = gd['balls']
            players = gd['players']
            weapons = gd['weapons']
            state = build_state_obj(balls, players, weapons)
        elif play_mode == PlayMode.REPLAY:
            replay_data = read_balls_players_weapons_events_from_file(gd)
            if replay_data:
                balls, players, weapons, replay_events = replay_data
            else:
                print(f"DEBUG stopping by no-replay-data.")
                gd['game_result'] = GAME_RESULT_REASON_NO_MORE_REPLAY_LOG
                running = False

        if running:
            is_quit_clicked, is_esc_pressed = read_events_and_apply_changes(gd, play_mode, replay_events)
            if is_quit_clicked:
                gd['game_result'] = GAME_RESULT_REASON_QUIT
                replay_running = False
                running = False
            if is_esc_pressed:
                gd['game_result'] = GAME_RESULT_REASON_ESCAPE_KEY
                replay_running = False
                running = False

        if play_mode == PlayMode.NEW:
            new_snapshot = build_snapshot_obj(state, gd['events'])
            save_snapshot(gd, new_snapshot)
            if online:
                send_snapshot_to_server(gd['sock'], new_snapshot)

        update_player_position(gd, dt)
        update_weapons_position(gd)
        update_ball_position(gd)

        if running:
            running = handle_conflicts(gd)

        draw_objects(gd)
        remaining_time = get_remaining_time_in_secs(gd)
        if display_timer:
            draw_timer(gd, remaining_time)

        if center_msg != "":
            display_press_escape_msg(gd, center_msg)
        if len(balls) == 0:
            gd['game_result'] = GAME_RESULT_REASON_SUCCESS
            running = False
        if remaining_time <= 0:
            gd['game_result'] = GAME_RESULT_REASON_TIMEOVER
            running = False

        pygame.display.update()
        # end of while

    if play_mode != PlayMode.REPLAY:
        display_game_result(gd)

    if play_mode == PlayMode.NEW:
        print(f"DEBUG game_result = {gd['game_result']}")
        if online:
            send_score_to_server(gd['sock'], username, gd['score'])
            gd['sock'].close()

    return replay_running, is_quit_clicked, is_esc_pressed


def start_game(online: bool = False):
    pygame.init()
    pygame.display.set_caption("PANG")

    while True:
        # 1
        is_quit_clicked = False
        running = True
        while running:
            game_loop_result = game_loop(play_mode=PlayMode.REPLAY,
                                         online=False,
                                         replay_file="data/replay.json",
                                         center_msg="Press ESCAPE key to start game",
                                         display_timer=False)
            if opts["debug"]:
                print(f"DEBUG 1 game_loop_result = {game_loop_result}")
            running, is_quit_clicked, is_esc_pressed = game_loop_result
            # True, False, False: Demo terminated. Continue demoing.
            # False, True, False: QUIT clicked. Terminate app.
            # False, False, True: Quit demo. Continue below to play game.
        if is_quit_clicked:
            if opts["debug"]:
                print(f"DEBUG 1 exiting")
            break
        pygame.time.delay(1000)

        print(f"DEBUG Starting a new game")
        game_loop_result = game_loop(play_mode=PlayMode.NEW,
                                     online=online,
                                     replay_file="data/recording.json")
        if opts["debug"]:
            print(f"DEBUG 2 game_loop_result = {game_loop_result}")
        running, is_quit_clicked, is_esc_pressed = game_loop_result
        if is_quit_clicked:
            if opts["debug"]:
                print(f"DEBUG 1 exiting")
            break
        pygame.time.delay(1000)

        # 3
        game_loop_result = game_loop(play_mode=PlayMode.REPLAY,
                                     online=False,
                                     replay_file="data/recording.json",
                                     center_msg="Enjoy your last play!")
        if opts["debug"]:
            print(f"DEBUG 3 game_loop_result = {game_loop_result}")
        running, is_quit_clicked, is_esc_pressed = game_loop_result
        if is_quit_clicked:
            if opts["debug"]:
                print(f"DEBUG 1 exiting")
            break
        pygame.time.delay(3000)

    pygame.quit()


if __name__ == "__main__":
    print(sys.path)
    opts = {"server_host": 'localhost', "server_port": 2345, "debug": False}
    parse_pang_client_ini_options(opts)
    parse_pang_client_cli_options(opts)
    print_options(opts)

    start_game(online=True)
