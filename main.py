from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BaseException):
    def __str__(self) -> str:
        return 'Выстрел за пределы поля'
    
class BoardUsedException(BaseException):
    def __str__(self) -> str:
        return 'Выстрел в ту же точку'
    
class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self) -> str:
        return f'Dot({self.x}, {self.y})'
    
class Ship:
    def __init__(self, bow, length, derection) -> None:
        self.bow = bow
        self.length = length
        self.derection = derection
        self.lives = length
    
    @property
    def dots(self):
        ship_dots = []
        
        for i in range(self.length):
            current_x = self.bow.x
            current_y = self.bow.y
            
            if self.derection == 0:
                current_x += i
            elif self.derection == 1:
                current_y += i
                
            ship_dots.append(Dot(current_x, current_y))
            
        return ship_dots
    
    def hit_verf(self, hit):
        return hit in self.dots

class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        
        self.count = 0
        
        self.field = [['0'] * size for _ in range(size)]
        
        self.busy = []
        self.ships = []
        
    def __str__(self) -> str:
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        
        for i, row in enumerate(self.field):
            res += f'\n{i+1} | ' + ' | '.join(row) + ' |'
            
        if self.hid:
            res = res.replace('■', '0')
        return res
    
    def out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))
    
    def contour(self, ship ,verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        
        for dot in ship.dots:
            for dot_x, dot_y in near:
                current = Dot(dot.x + dot_x, dot.y + dot_y)
                
                if not (self.out(current)) and current not in self.busy:
                    if verb:
                        self.field[current.x][current.y] = '.'
                    self.busy.append(current)
    
    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
            
        for dot in ship.dots:
            self.field[dot.x][dot.y] = '■'
            self.busy.append(dot)
            
            self.ships.append(ship)
            self.contour(ship)
    
    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        
        if dot in self.busy:
            raise BoardUsedException()
        
        self.busy.append(dot)
        
        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.field[dot.x][dot.y] = 'X'
                
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print('Корабль уничтожен')
                    return False
                else:
                    print('Корабль ранен')
                    return True
                
        self.field[dot.x][dot.y] = 'T'
        print('Промах')
        return False
    
    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
        
    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BaseException as e:
                print(e)

class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {dot.x+1} {dot.y+1}')
        return dot
    
class User(Player):
    def ask(self):
        while True:
            coords = input('Введите координаты: ').split()
            
            if len(coords) != 2:
                print('Введите 2 координаты')
                continue
            
            x, y = coords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print('Введите числа')
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)
        
class Game:
    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board
        
    
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)
        
    def greet(self):
        print('формат ввода: x y')
        print('x - номер строки')
        print('y - номер столбца')
        
    def loop(self):
        num = 0
        
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-"*20)
            
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
                
            if repeat:
                num -= 1
            
            if self.ai.board.count == 7:
                print("-"*20)
                print("Пользователь выиграл!")
                break
            
            if self.us.board.count == 7:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1
        
    def start(self):
        self.greet()
        self.loop()
        
game = Game()
game.start()
        