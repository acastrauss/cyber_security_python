import bitarray
from bitarray.util import ba2int
import string
import numpy as np
import copy
import sys

class Sha1():
    def __init__(self) -> None:
        self.H0 = 0X67DE2A01
        self.H1 = 0XBB03E28C
        self.H2 = 0X011EF1DC
        self.H3 = 0X9293E9E2
        self.H4 = 0XCDEF23A9
        # in bits
        self.chunk_size = 512
        # in bits
        self.word_size = 32
        self.baseBa = bitarray.bitarray()

    def digest(self, message) -> string:
        self._pad_message(message)
        for i in range(len(self.baseBa) // self.chunk_size):
            self._chunk_operation(self.baseBa[self.chunk_size * i: self.chunk_size * (i + 1)])

        final_digest = self._circular_shift(self.H0, 128) | self._circular_shift(self.H1, 96) | self._circular_shift(self.H2, 64) | self._circular_shift(self.H3, 32) | self.H4
        s = sys.getsizeof(final_digest)
        b = final_digest.to_bytes(s, 'little')
        print(f"Sha1 of {message} is {b.decode('utf-8')}")

    def _pad_message(self, message):
        self.baseBa.frombytes(message.encode('utf-8'))
        self.baseBa.append(0b1)
        tempLen = 448
        for i in range(tempLen - (len(self.baseBa) % tempLen)):
            self.baseBa.append(0b0)
        
        # len of message is 64bits
        temp = np.int64(len(message))
        tempBa = bitarray.bitarray()
        tempBa.frombytes(temp.tobytes())
        self.baseBa += tempBa
        # after this bitarray should have 512 bits

    def _circular_shift(self, word, degree):
        bitlength = 0
        if type(word) is bitarray.bitarray:
            bitlength = len(word)
        else: # word is number
            bitlength = word.bit_length()

        return (word << degree) | (word >> bitlength - degree)

    def _chunk_operation(self, chunck: bitarray.bitarray): 
        chunck_words: list[bitarray.bitarray] = []

        for i in range(len(chunck) // self.word_size):
            tempBa = bitarray.bitarray()
            tempBa = chunck[i * self.word_size: (i+1) * self.word_size]
            chunck_words.append(tempBa)

        for i in range(16, 80+1):
            chunck_words.append(self._circular_shift(
                chunck_words[i-3] ^ chunck_words[i-8] ^ chunck_words[i-14] ^ chunck_words[i-16], 1
            ))

        A = copy.deepcopy(self.H0)
        B = copy.deepcopy(self.H1)
        C = copy.deepcopy(self.H2)
        D = copy.deepcopy(self.H3)
        E = copy.deepcopy(self.H4)
        
        for i in range(80):
            if 0 <= i <= 19:
                f = D ^ ((B & C) | (~B & D))
                k = 0x5A827999
            elif 20 <= i <= 39:
                f = B ^ C ^ D
                k = 0x6ED9EBA1
            elif 40 <= i <= 59:
                f = (B & C) | (B & D) | (C & D)
                k = 0x8F1BBCDC
            elif 60 <= i <= 79:
                f = B ^ C ^ D
                k = 0xCA62C1D6
                
            temp = self._circular_shift(
                A + f + E + ba2int(chunck_words[i]) + k 
                , 5
            )
            E = D
            D = C
            C = self._circular_shift(B, 30)
            B = A
            A = temp

        self.H0 += A
        self.H1 += B
        self.H2 += C
        self.H3 += D
        self.H4 += E
