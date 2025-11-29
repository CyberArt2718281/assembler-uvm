#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ассемблер для УВМ (Вариант №15)
Этапы 1-2: Трансляция из языка ассемблера в машинный код
"""

import sys
import struct
from typing import List, Dict, Tuple


class Instruction:
    """Базовый класс для команды"""
    def __init__(self, opcode: int):
        self.opcode = opcode
    
    def to_bytes(self) -> bytes:
        """Преобразование в байты"""
        raise NotImplementedError
    
    def __repr__(self):
        return f"{self.__class__.__name__}(opcode={self.opcode})"


class LoadConstInstruction(Instruction):
    """Загрузка константы: LOAD_CONST константа адрес"""
    def __init__(self, constant: int, address: int):
        super().__init__(111)  # Код операции = 111
        self.constant = constant  # 11 бит (биты 7-17)
        self.address = address    # 26 бит (биты 18-43)
        
        # Проверка диапазонов
        if not (0 <= constant < 2048):
            raise ValueError(f"Константа {constant} вне диапазона [0, 2047]")
        if not (0 <= address < 67108864):
            raise ValueError(f"Адрес {address} вне диапазона [0, 67108863]")
    
    def to_bytes(self) -> bytes:
        """
        Формат: A(0-6)=111, B(7-17)=constant, C(18-43)=address
        Размер: 6 байт = 48 бит
        """
        # Собираем все биты в одно число
        value = self.opcode | (self.constant << 7) | (self.address << 18)
        
        # Преобразуем в 6 байт (little-endian)
        return value.to_bytes(6, byteorder='little')
    
    def __repr__(self):
        return f"LOAD_CONST(A={self.opcode}, B={self.constant}, C={self.address})"


class ReadMemInstruction(Instruction):
    """Чтение из памяти: READ_MEM смещение адрес_источника адрес_назначения"""
    def __init__(self, offset: int, src_addr: int, dst_addr: int):
        super().__init__(40)  # Код операции = 40
        self.offset = offset      # 8 бит (биты 7-14)
        self.src_addr = src_addr  # 26 бит (биты 15-40)
        self.dst_addr = dst_addr  # 26 бит (биты 41-66)
        
        # Проверка диапазонов
        if not (0 <= offset < 256):
            raise ValueError(f"Смещение {offset} вне диапазона [0, 255]")
        if not (0 <= src_addr < 67108864):
            raise ValueError(f"Адрес {src_addr} вне диапазона [0, 67108863]")
        if not (0 <= dst_addr < 67108864):
            raise ValueError(f"Адрес {dst_addr} вне диапазона [0, 67108863]")
    
    def to_bytes(self) -> bytes:
        """
        Формат: A(0-6)=40, B(7-14)=offset, C(15-40)=src_addr, D(41-66)=dst_addr
        Размер: 9 байт = 72 бита (используем 67 бит)
        """
        value = self.opcode | (self.offset << 7) | (self.src_addr << 15) | (self.dst_addr << 41)
        return value.to_bytes(9, byteorder='little')
    
    def __repr__(self):
        return f"READ_MEM(A={self.opcode}, B={self.offset}, C={self.src_addr}, D={self.dst_addr})"


class WriteMemInstruction(Instruction):
    """Запись в память: WRITE_MEM адрес_источника адрес_назначения"""
    def __init__(self, src_addr: int, dst_addr: int):
        super().__init__(101)  # Код операции = 101
        self.src_addr = src_addr  # 26 бит (биты 7-32)
        self.dst_addr = dst_addr  # 26 бит (биты 33-58)
        
        # Проверка диапазонов
        if not (0 <= src_addr < 67108864):
            raise ValueError(f"Адрес {src_addr} вне диапазона [0, 67108863]")
        if not (0 <= dst_addr < 67108864):
            raise ValueError(f"Адрес {dst_addr} вне диапазона [0, 67108863]")
    
    def to_bytes(self) -> bytes:
        """
        Формат: A(0-6)=101, B(7-32)=src_addr, C(33-58)=dst_addr
        Размер: 8 байт = 64 бита (используем 59 бит)
        """
        value = self.opcode | (self.src_addr << 7) | (self.dst_addr << 33)
        return value.to_bytes(8, byteorder='little')
    
    def __repr__(self):
        return f"WRITE_MEM(A={self.opcode}, B={self.src_addr}, C={self.dst_addr})"


class GTEInstruction(Instruction):
    """Операция >=: GTE смещение1 адрес1 адрес2 адрес_рез смещение2"""
    def __init__(self, offset1: int, addr1: int, addr2: int, res_addr: int, offset2: int):
        super().__init__(68)  # Код операции = 68
        self.offset1 = offset1    # 8 бит (биты 7-14)
        self.addr1 = addr1        # 26 бит (биты 15-40)
        self.addr2 = addr2        # 26 бит (биты 41-66)
        self.res_addr = res_addr  # 26 бит (биты 67-92)
        self.offset2 = offset2    # 8 бит (биты 93-100)
        
        # Проверка диапазонов
        if not (0 <= offset1 < 256):
            raise ValueError(f"Смещение1 {offset1} вне диапазона [0, 255]")
        if not (0 <= offset2 < 256):
            raise ValueError(f"Смещение2 {offset2} вне диапазона [0, 255]")
        if not (0 <= addr1 < 67108864):
            raise ValueError(f"Адрес1 {addr1} вне диапазона [0, 67108863]")
        if not (0 <= addr2 < 67108864):
            raise ValueError(f"Адрес2 {addr2} вне диапазона [0, 67108863]")
        if not (0 <= res_addr < 67108864):
            raise ValueError(f"Адрес результата {res_addr} вне диапазона [0, 67108863]")
    
    def to_bytes(self) -> bytes:
        """
        Формат: A(0-6)=68, B(7-14)=offset1, C(15-40)=addr1, 
                D(41-66)=addr2, E(67-92)=res_addr, F(93-100)=offset2
        Размер: 13 байт = 104 бита (используем 101 бит)
        """
        value = (self.opcode | 
                (self.offset1 << 7) | 
                (self.addr1 << 15) | 
                (self.addr2 << 41) | 
                (self.res_addr << 67) | 
                (self.offset2 << 93))
        return value.to_bytes(13, byteorder='little')
    
    def __repr__(self):
        return (f"GTE(A={self.opcode}, B={self.offset1}, C={self.addr1}, "
                f"D={self.addr2}, E={self.res_addr}, F={self.offset2})")


class Assembler:
    """Ассемблер для УВМ"""
    
    def __init__(self):
        self.instructions: List[Instruction] = []
    
    def parse_line(self, line: str) -> Instruction:
        """Разбор одной строки ассемблера"""
        # Убираем комментарии
        if '#' in line:
            line = line[:line.index('#')]
        
        # Убираем пробелы
        line = line.strip()
        if not line:
            return None
        
        # Разбиваем на токены
        tokens = line.split()
        if not tokens:
            return None
        
        mnemonic = tokens[0].upper()
        args = tokens[1:]
        
        try:
            if mnemonic == "LOAD_CONST":
                if len(args) != 2:
                    raise ValueError(f"LOAD_CONST требует 2 аргумента, получено {len(args)}")
                constant = int(args[0])
                address = int(args[1])
                return LoadConstInstruction(constant, address)
            
            elif mnemonic == "READ_MEM":
                if len(args) != 3:
                    raise ValueError(f"READ_MEM требует 3 аргумента, получено {len(args)}")
                offset = int(args[0])
                src_addr = int(args[1])
                dst_addr = int(args[2])
                return ReadMemInstruction(offset, src_addr, dst_addr)
            
            elif mnemonic == "WRITE_MEM":
                if len(args) != 2:
                    raise ValueError(f"WRITE_MEM требует 2 аргумента, получено {len(args)}")
                src_addr = int(args[0])
                dst_addr = int(args[1])
                return WriteMemInstruction(src_addr, dst_addr)
            
            elif mnemonic == "GTE":
                if len(args) != 5:
                    raise ValueError(f"GTE требует 5 аргументов, получено {len(args)}")
                offset1 = int(args[0])
                addr1 = int(args[1])
                addr2 = int(args[2])
                res_addr = int(args[3])
                offset2 = int(args[4])
                return GTEInstruction(offset1, addr1, addr2, res_addr, offset2)
            
            else:
                raise ValueError(f"Неизвестная мнемоника: {mnemonic}")
        
        except ValueError as e:
            raise ValueError(f"Ошибка в строке '{line}': {e}")
    
    def assemble(self, source: str) -> List[Instruction]:
        """Ассемблирование программы"""
        self.instructions = []
        
        for line_num, line in enumerate(source.split('\n'), 1):
            try:
                instr = self.parse_line(line)
                if instr:
                    self.instructions.append(instr)
            except ValueError as e:
                print(f"Ошибка в строке {line_num}: {e}", file=sys.stderr)
                raise
        
        return self.instructions
    
    def to_binary(self) -> bytes:
        """Преобразование в машинный код"""
        binary = b''
        for instr in self.instructions:
            binary += instr.to_bytes()
        return binary


def main():
    if len(sys.argv) < 3:
        print("Использование: python assembler.py <входной_файл.asm> <выходной_файл.bin> [--test]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = '--test' in sys.argv
    
    # Чтение исходного кода
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден", file=sys.stderr)
        sys.exit(1)
    
    # Ассемблирование
    assembler = Assembler()
    try:
        instructions = assembler.assemble(source)
    except ValueError as e:
        print(f"Ошибка ассемблирования: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Режим тестирования: вывод промежуточного представления
    if test_mode:
        print("=== Промежуточное представление ===")
        for i, instr in enumerate(instructions):
            print(f"{i}: {instr}")
        print()
    
    # Генерация машинного кода
    binary = assembler.to_binary()
    
    # Запись в файл
    with open(output_file, 'wb') as f:
        f.write(binary)
    
    print(f"Ассемблирование завершено успешно")
    print(f"Размер выходного файла: {len(binary)} байт")
    
    # В режиме тестирования выводим байты
    if test_mode:
        print("\n=== Машинный код (байты) ===")
        for i, instr in enumerate(instructions):
            instr_bytes = instr.to_bytes()
            hex_str = ', '.join(f'0x{b:02X}' for b in instr_bytes)
            print(f"{i}: {hex_str}")
            print(f"   {instr}")


if __name__ == '__main__':
    main()
