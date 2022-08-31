import gym
from gym import spaces
from . import adversarial

import chess
import chess.svg

import numpy as np

from io import BytesIO
import cairosvg
from PIL import Image


class ChessActionSpace(adversarial.AdversarialActionSpace):
    def __init__(self, board):
        self.board = board

    def sample(self):
        moves = list(self.board.legal_moves)
        move = np.random.choice(moves)
        return ChessEnv._move_to_action(move)

    @property
    def legal_actions(self):
        return [ChessEnv._move_to_action(move) for move in self.board.legal_moves]


class ChessEnv(adversarial.AdversarialEnv):
    """Chess Environment"""
    metadata = {'render.modes': ['rgb_array', 'human']}

    def __init__(self, render_size=512, observation_mode='piece_map', claim_draw=True, **kwargs):
        super(ChessEnv, self).__init__()
        self.board = chess.Board(chess960=False)

        self.action_space = ChessActionSpace(self.board)
        self.observation_space = spaces.Box(low=-6, high=6,
                                            shape=(8, 8),
                                            dtype=np.uint8)

        self.render_size = render_size
        self.claim_draw = claim_draw
        self.viewer = None
    
    @property
    def current_player(self):
        return self.board.turn

    @property
    def previous_player(self):
        return not self.board.turn

    def get_string_representation(self):
        return self.board.fen()
    
    def set_string_representation(self, board_string):
        self.board = chess.Board(board_string)
        self.action_space = ChessActionSpace(self.board)

    def get_canonical_observaion(self):
        state = (self.get_piece_configuration(self.board))
        player = self.current_player

        canonical_state = state[::-1,::-1] if player == chess.BLACK else state

        return (-1)**player * canonical_state

    def game_result(self):
        result = self.board.result()
        return (chess.WHITE if result == '1-0' else chess.BLACK if result ==
                  '0-1' else -1 if result == '1/2-1/2' else None)

    def step(self, action):
        move = self._action_to_move(action)
        self.board.push(move)

        observation = self.get_canonical_observaion()
        player = self.current_player
        result = self.game_result()
        # Reward is 1 for white win or -1 for black win
        reward = 0 if result is None else 1
        done = result is not None
        info = {'player': player,
                'castling_rights': self.board.castling_rights,
                'fullmove_number': self.board.fullmove_number,
                'halfmove_clock': self.board.halfmove_clock,
                'promoted': self.board.promoted,
                'ep_square': self.board.ep_square}

        return observation, reward, done, info

    def reset(self):
        self.board.reset()
        return self.get_canonical_observaion()

    def render(self, mode='human'):
        out = BytesIO()
        bytestring = chess.svg.board(
            self.board, size=self.render_size).encode('utf-8')
        cairosvg.svg2png(bytestring=bytestring, write_to=out)
        image = Image.open(out)
        img = np.asarray(image)

        if mode == 'rgb_array':
            return img
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(img)
            return self.viewer.isopen

    def close(self):
        if not self.viewer is None:
            self.viewer.close()

    @staticmethod
    def get_piece_configuration(board):
        piece_map = np.zeros(64, dtype=np.int8)

        for square, piece in zip(board.piece_map().keys(), board.piece_map().values()):
            piece_map[square] = piece.piece_type * ((-1)**piece.color)

        return piece_map.reshape((8, 8))

    @staticmethod
    def _action_to_move(action):
        from_square = chess.Square(action[0])
        to_square = chess.Square(action[1])
        promotion = (None if action[2] == 0 else chess.PieceType(action[2]))
        move = chess.Move(from_square, to_square, promotion)
        return move

    @staticmethod
    def _move_to_action(move):
        from_square = move.from_square
        to_square = move.to_square
        promotion = (0 if move.promotion is None else move.promotion)
        return np.array([from_square, to_square, promotion])
