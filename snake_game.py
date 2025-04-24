import pygame
import random
import psycopg2
import pickle

# PostgreSQL-ге қосылу
def connect_db():
    return psycopg2.connect(
        dbname="postgres",       # Базаның атын өзгертуге болады (мысалы, snake_game)
        user="ayala",
        password="ayala1234",    # Өз пароліңді орнатқаныңды қолданысқа енгіз
        host="localhost",
        port="5432"
    )

# Ойынның параметрлері
WIDTH, HEIGHT = 640, 480
SNAKE_SIZE = 10
SNAKE_SPEED = 15

# Pygame бастауды орнату
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')

# Түстерді анықтау
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Қозғалу функциясы
def draw_snake(snake_size, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_size, snake_size])

def game_over(score):
    font_style = pygame.font.SysFont("bahnschrift", 25)
    msg = font_style.render("Game Over! Your Score: " + str(score), True, RED)
    screen.blit(msg, [WIDTH / 6, HEIGHT / 3])
    pygame.display.update()
    pygame.time.wait(2000)

# Пайдаланушыны сұрау
def get_user():
    conn = connect_db()
    cursor = conn.cursor()
    username = input("Enter your username: ")

    cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
    user = cursor.fetchone()

    if user:
        print(f"Welcome back, {username}! Current level: {user[2]}")
        return username, user[2]  # қайтару username мен current level
    else:
        cursor.execute("INSERT INTO users (username, level, score) VALUES (%s, %s, %s) RETURNING id;", (username, 1, 0))
        conn.commit()
        user_id = cursor.fetchone()[0]
        print(f"New user created. Welcome, {username}!")
        return username, 1  # жаңа пайдаланушы үшін level = 1

def save_game_state(username, level, score):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET level = %s, score = %s
        WHERE username = %s;
    """, (level, score, username))

    conn.commit()
    cursor.close()
    conn.close()

def game_loop():
    username, level = get_user()
    score = 0

    snake_position = [100, 50]
    snake_body = [[100, 50], [90, 50], [80, 50]]

    food_position = [random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
                     random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE]
    food_spawn = True

    direction = 'RIGHT'
    change_to = direction

    clock = pygame.time.Clock()
    game_over_flag = False

    while not game_over_flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over_flag = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_to = 'UP'
                if event.key == pygame.K_DOWN:
                    change_to = 'DOWN'
                if event.key == pygame.K_LEFT:
                    change_to = 'LEFT'
                if event.key == pygame.K_RIGHT:
                    change_to = 'RIGHT'
                if event.key == pygame.K_p:  # Pause and save game state
                    save_game_state(username, level, score)
                    print("Game paused and state saved.")

        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        if direction == 'UP':
            snake_position[1] -= SNAKE_SIZE
        if direction == 'DOWN':
            snake_position[1] += SNAKE_SIZE
        if direction == 'LEFT':
            snake_position[0] -= SNAKE_SIZE
        if direction == 'RIGHT':
            snake_position[0] += SNAKE_SIZE

        snake_body.insert(0, list(snake_position))
        if snake_position[0] == food_position[0] and snake_position[1] == food_position[1]:
            score += 10
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_position = [random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
                             random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE]
        food_spawn = True

        screen.fill(BLUE)
        draw_snake(SNAKE_SIZE, snake_body)

        pygame.draw.rect(screen, RED, [food_position[0], food_position[1], SNAKE_SIZE, SNAKE_SIZE])

        if snake_position[0] < 0 or snake_position[0] > WIDTH - SNAKE_SIZE or snake_position[1] < 0 or snake_position[1] > HEIGHT - SNAKE_SIZE:
            game_over(score)
            game_over_flag = True

        for block in snake_body[1:]:
            if block == snake_position:
                game_over(score)
                game_over_flag = True

        pygame.display.update()
        clock.tick(SNAKE_SPEED)

    save_game_state(username, level, score)

# Мәліметтер базасын және кестелерді жасау
def setup_database():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            level INT DEFAULT 1,
            score INT DEFAULT 0
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

# Негізгі функция
if __name__ == "__main__":
    setup_database()  # Базаны құру
    game_loop()       # Ойынды бастау
    pygame.quit()
