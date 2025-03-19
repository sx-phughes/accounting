import numpy as np

def code_algo(num: int, shift: int):
    return num + shift

def encrypt(s: str, shift: int):
    unicode = [int(x) for x in s.encode('utf-8')]
    
    encrypted = [code_algo(x, shift) for x in unicode]
    
    encrypted_string = ''.join(chr(x) for x in encrypted)
    
    return encrypted_string
    
def bin_to_num(bin: str):
    bin_list = [int(x) for x in bin]
    
    bin_vector = [np.power(2, x) for x in range(len(bin_list))]
    bin_vector.reverse()
    
    bin_components = [bit * power for bit, power in zip(bin_list, bin_vector)]
    
    num = sum(bin_components)
    
    return num

def rounddown(num: float) -> int:
    return int(num - (num % 1))

def div_and_rem(dividend: int, divisor: int):
    rem = dividend % divisor
    quotient = rounddown(dividend / divisor)
    
    return (quotient, rem)
    
def num_to_bin(num: int):
    bit_list = []
    
    rem = num
    
    while rem > 0:
        div, bin = div_and_rem(rem, 2)
        bit_list.append(bin)
        rem = div
    
    str_bits = [str(bit) for bit in bit_list]
    str_bits.reverse()
    binary = ''.join(str_bits)
    
    return binary

def bits_to_bytes(bits: str):
    b = []
    
    whole_bytes, partial_bytes = div_and_rem(len(bits), 8)
    
    zero_pad = '0' * (8 - partial_bytes)
    
    padded_bits = zero_pad + bits
    
    for i in range(len(padded_bits)/(8)):
        start = i * 8
        stop = (i + 1) * 8
        b_x = bits[start:stop]
        b.append(b_x)
        
    return b
    
def decrypt(s: str, shift: int):
    ords = [ord(x) for x in s]
    
    bytes_decoded = [code_algo(x, shift) for x in ords]
    
    chars = [chr(x) for x in bytes_decoded]
    
    return ''.join(chars)