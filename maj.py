import numpy as np

TILE_ID = {
    '1p': 0,
    '2p': 1,
    '3p': 2,
    '4p': 3,
    '5p': 4,
    '6p': 5,
    '7p': 6,
    '8p': 7,
    '9p': 8,
    '1m': 9,
    '2m': 10,
    '3m': 11,
    '4m': 12,
    '5m': 13,
    '6m': 14,
    '7m': 15,
    '8m': 16,
    '9m': 17,
    '1s': 18,
    '2s': 19,
    '3s': 20,
    '4s': 21,
    '5s': 22,
    '6s': 23,
    '7s': 24,
    '8s': 25,
    '9s': 26,
    'do': 27,
    'na': 28,
    'xi': 29,
    'be': 30,
    'ba': 31,
    'zh': 32,
    'fa': 33,
}

TILE_ID_INVERSE = {
    0: '1p',
    1: '2p',
    2: '3p',
    3: '4p',
    4: '5p',
    5: '6p',
    6: '7p',
    7: '8p',
    8: '9p',
    9: '1m',
    10: '2m',
    11: '3m',
    12: '4m',
    13: '5m',
    14: '6m',
    15: '7m',
    16: '8m',
    17: '9m',
    18: '1s',
    19: '2s',
    20: '3s',
    21: '4s',
    22: '5s',
    23: '6s',
    24: '7s',
    25: '8s',
    26: '9s',
    27: 'do',
    28: 'na',
    29: 'xi',
    30: 'be',
    31: 'ba',
    32: 'zh',
    33: 'fa',
}

INTERNAL_TILES = {
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
}

EXTERNAL_TILES = {
    0,
    8,
    9,
    17,
    18,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
}

PONG = 0
CHOW = 1

def encode(s):
    '''
    Encode s into an internal representation.
    '''
    return TILE_ID[s]

def decode(r):
    '''
    Decodes r into a string.
    '''
    if type(r) is tuple:
        if type(r[1]) is tuple:
            return (r[0],) + tuple(map(decode, r[1]))
        else:
            return tuple(map(decode, r))
    return TILE_ID_INVERSE[r]

class Mountain:
    def __init__(self, skip_init=False):
        
        self.tile_matrix = None
        self.meld_matrix = None
        self.pair_matrix = None

        if skip_init:
            return

        ones = np.ones(34, dtype=np.uint8)
        tile_matrix = 4 * ones

        self.tile_matrix = tile_matrix

        meld_matrix = np.vstack((ones, ones))
        meld_matrix[PONG] *= 4
        meld_matrix[CHOW] *= 64
        for c in EXTERNAL_TILES:
            meld_matrix[CHOW, c] = 0
        
        self.meld_matrix = meld_matrix

        pair_matrix = 6 * ones

        self.pair_matrix = pair_matrix

    def copy(self):
        cpy = Mountain(True)
        cpy.tile_matrix = self.tile_matrix.copy()
        cpy.meld_matrix = self.meld_matrix.copy()
        cpy.pair_matrix = self.pair_matrix.copy()
        return cpy

    def remove(self, c):
        if self.tile_matrix[c] == 0:
            import pdb; pdb.set_trace()
        self.tile_matrix[c] -= 1

        n = self.tile_matrix[c]
        if n == 3:
            self.pair_matrix[c] = 3
            self.meld_matrix[PONG, c] = 1
        elif n == 2:
            self.pair_matrix[c] = 1
            self.meld_matrix[PONG, c] = 0
            self.on_pong_elimination(c)
        elif n == 1:
            self.pair_matrix[c] = 0
            self.on_pair_elimination(c)

        if c-1 in INTERNAL_TILES:
            m = self.tile_matrix[c-2] * self.tile_matrix[c-1] * self.tile_matrix[c]
            self.meld_matrix[CHOW, c-1] = m
            if m == 0:
                self.on_chow_elimination(c-1)

        if c in INTERNAL_TILES:
            m = self.tile_matrix[c-1] * self.tile_matrix[c] * self.tile_matrix[c+1]
            self.meld_matrix[CHOW, c] = m
            if m == 0:
                self.on_chow_elimination(c)

        if c+1 in INTERNAL_TILES:
            m = self.tile_matrix[c] * self.tile_matrix[c+1] * self.tile_matrix[c+2]
            self.meld_matrix[CHOW, c+1] = m
            if m == 0:
                self.on_chow_elimination(c+1)

    def insert(self, c):
        n = self.tile_matrix[c]
        assert n < 4 and n >= 0
        
        self.tile_matrix[c] += 1
        n +=1

        if n == 4:
            self.pair_matrix[c] = 6
            self.meld_matrix[PONG, c] = 4
        elif n == 3:
            self.pair_matrix[c] = 3
            self.meld_matrix[PONG, c] = 1
        elif n == 2:
            self.pair_matrix[c] = 1
        elif n == 1:
            pass

        if c-1 in INTERNAL_TILES:
            m = self.tile_matrix[c-2] * self.tile_matrix[c-1] * self.tile_matrix[c]
            self.meld_matrix[CHOW, c-1] = m
            if m == 0:
                self.on_chow_elimination(c-1)

        if c in INTERNAL_TILES:
            m = self.tile_matrix[c-1] * self.tile_matrix[c] * self.tile_matrix[c+1]
            self.meld_matrix[CHOW, c] = m
            if m == 0:
                self.on_chow_elimination(c)

        if c+1 in INTERNAL_TILES:
            m = self.tile_matrix[c] * self.tile_matrix[c+1] * self.tile_matrix[c+2]
            self.meld_matrix[CHOW, c+1] = m
            if m == 0:
                self.on_chow_elimination(c+1)

    def p2(self):
        '''
        Samples a pair (uniformly random) from the mountain.

        Returns a tuple t:
            t[0] denotes the probability of such choice
            t[1] a tuple such that t[1][0] and t[1][1] denotes the pair
        '''
        total = np.sum(self.pair_matrix, dtype=np.float)
        assert total > 0
        
        prob_matrix = self.pair_matrix / total
        c = np.random.choice(34, p=prob_matrix)
        p = prob_matrix[c]
        self.remove(c)

        return (p, (c, c))
        
    def p3(self):
        '''
        Samples a meld (uniformly random) from the mountain.
        
        Returns a tuple t:
            t[0] denotes the probability of such choice
            t[1] a tuple such that t[1][0] t[1][1] and t[1][2] denotes the meld
        '''
        total_pong = np.sum(self.meld_matrix[PONG, :], dtype=np.float)
        total_chow = np.sum(self.meld_matrix[CHOW, :], dtype=np.float)
        total = np.sum(self.meld_matrix, dtype=np.float)
        assert total_pong > 0 or total_chow > 0

        prob_matrix = np.zeros(2, dtype=np.float)
        prob_matrix[PONG] = total_pong / total
        prob_matrix[CHOW] = total_chow / total

        p = None
        t = None
        c = np.random.choice(2, p=prob_matrix)
        if c == PONG:
            p = prob_matrix[PONG]
            t = self.p3_pong(total_pong)
        else:
            p = prob_matrix[CHOW]
            t = self.p3_chow(total_chow)

        return (p * t[0], t[1])

    def p3_pong(self, total):
        prob_matrix = self.meld_matrix[PONG, :] / total
        c = np.random.choice(34, p=prob_matrix)
        p = prob_matrix[c]
        self.remove(c)
        self.remove(c)
        self.remove(c)

        return (p, (c, c, c))

    def p3_chow(self, total):
        prob_matrix = self.meld_matrix[CHOW, :] / total
        c = np.random.choice(34, p=prob_matrix)
        p = prob_matrix[c]
        self.remove(c-1)
        self.remove(c)
        self.remove(c+1)

        return (p, (c-1, c, c+1))

    def __str__(self):
        s = ''
        total_pong = np.sum(self.meld_matrix[PONG, :], dtype=np.float)
        total_chow = np.sum(self.meld_matrix[CHOW, :], dtype=np.float)
        total_pair = np.sum(self.pair_matrix, dtype=np.float)
        total = total_pong + total_chow + total_pair

        s += 'PONG p {}\n'.format(self.meld_matrix[PONG, 0:9])
        s += 'PONG m {}\n'.format(self.meld_matrix[PONG, 9:18])
        s += 'PONG s {}\n'.format(self.meld_matrix[PONG, 18:27])
        s += 'PONG z {}\n'.format(self.meld_matrix[PONG, 27:])
        s += 'CHOW p {}\n'.format(self.meld_matrix[CHOW, 0:9])
        s += 'CHOW m {}\n'.format(self.meld_matrix[CHOW, 9:18])
        s += 'CHOW s {}\n'.format(self.meld_matrix[CHOW, 18:27])
        s += 'PAIR p {}\n'.format(self.pair_matrix[0:9])
        s += 'PAIR m {}\n'.format(self.pair_matrix[9:18])
        s += 'PAIR s {}\n'.format(self.pair_matrix[18:27])
        s += 'PAIR z {}'.format(self.pair_matrix[27:])

        return s

    def on_pong_elimination(self, c):
        print('PONG {} is eliminated'.format(decode((c, c, c))))

    def on_chow_elimination(self, c):
        print('CHOW {} is eliminated'.format(decode((c-1, c, c+1))))

    def on_pair_elimination(self, c):
        print('PAIR {} is eliminated'.format(decode((c, c))))

def trial(m, lst):
    for i in range(len(lst)):
        mc = m.copy()
        print()
        print('deal', lst[i])
        for j in range(len(lst)):
            if i == j:
                continue
            else:
                mc.remove(encode(lst[j]))
        print(mc)
        a = mc.meld_matrix[PONG,encode(lst[i])]
        b = mc.meld_matrix[CHOW,encode(lst[i])]
        c = mc.pair_matrix[encode(lst[i])]
        print(
            'weakness (PONG, CHOW, PAIR, probability)', 
            a, 
            b, 
            c,
            (a+b+c) / (mc.pair_matrix.sum() + mc.meld_matrix.sum())
        )
        
