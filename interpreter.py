#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерпретатор для УВМ (Вариант №15)
Этапы 3-4: Выполнение программ УВМ
"""

import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict


class VirtualMachine:
    """Виртуальная машина с разделённой памятью"""
    
    def __init__(self, memory_size=100000):
        """Инициализация УВМ"""
        self.data_memory = [0] * memory_size  # Память данных
        self.code_memory = b''  # Память команд (бинарный код)
        self.pc = 0  # Program Counter (указатель на текущую команду в байтах)
    
    def load_program(self, binary_code: bytes):
        """Загрузка программы в память команд"""
        self.code_memory = binary_code
        self.pc = 0
    
    def read_bits(self, start_bit: int, length: int) -> int:
        """Чтение битового поля из текущей позиции в памяти команд"""
        # Вычисляем байты, которые нужно прочитать
        start_byte = start_bit // 8
        end_byte = (start_bit + length - 1) // 8 + 1
        
        # Читаем нужные байты
        bytes_to_read = self.code_memory[self.pc + start_byte:self.pc + end_byte]
        
        # Преобразуем в число
        value = int.from_bytes(bytes_to_read, byteorder='little')
        
        # Вычисляем смещение и маску
        bit_offset = start_bit % 8
        mask = (1 << length) - 1
        
        # Извлекаем нужные биты
        return (value >> bit_offset) & mask
    
    def execute_load_const(self):
        """Выполнение команды LOAD_CONST"""
        # A(0-6)=111, B(7-17)=constant, C(18-43)=address
        opcode = self.read_bits(0, 7)
        constant = self.read_bits(7, 11)
        address = self.read_bits(18, 26)
        
        # Загружаем константу в память
        self.data_memory[address] = constant
        
        # Перемещаем PC на 6 байт
        self.pc += 6
        
        return f"LOAD_CONST: [{address}] = {constant}"
    
    def execute_read_mem(self):
        """Выполнение команды READ_MEM"""
        # A(0-6)=40, B(7-14)=offset, C(15-40)=src_addr, D(41-66)=dst_addr
        opcode = self.read_bits(0, 7)
        offset = self.read_bits(7, 8)
        src_addr = self.read_bits(15, 26)
        dst_addr = self.read_bits(41, 26)
        
        # Вычисляем эффективный адрес
        effective_addr = self.data_memory[src_addr] + offset
        
        # Читаем значение и записываем в целевой адрес
        value = self.data_memory[effective_addr]
        self.data_memory[dst_addr] = value
        
        # Перемещаем PC на 9 байт
        self.pc += 9
        
        return f"READ_MEM: [{dst_addr}] = memory[memory[{src_addr}] + {offset}] = memory[{effective_addr}] = {value}"
    
    def execute_write_mem(self):
        """Выполнение команды WRITE_MEM"""
        # A(0-6)=101, B(7-32)=src_addr, C(33-58)=dst_addr
        opcode = self.read_bits(0, 7)
        src_addr = self.read_bits(7, 26)
        dst_addr = self.read_bits(33, 26)
        
        # Копируем значение из src в dst
        value = self.data_memory[src_addr]
        self.data_memory[dst_addr] = value
        
        # Перемещаем PC на 8 байт
        self.pc += 8
        
        return f"WRITE_MEM: [{dst_addr}] = [{src_addr}] = {value}"
    
    def execute_gte(self):
        """Выполнение команды GTE (>=)"""
        # A(0-6)=68, B(7-14)=offset1, C(15-40)=addr1, D(41-66)=addr2,
        # E(67-92)=res_addr, F(93-100)=offset2
        opcode = self.read_bits(0, 7)
        offset1 = self.read_bits(7, 8)
        addr1 = self.read_bits(15, 26)
        addr2 = self.read_bits(41, 26)
        res_addr = self.read_bits(67, 26)
        offset2 = self.read_bits(93, 8)
        
        # Вычисляем эффективные адреса
        effective_addr1 = self.data_memory[addr1] + offset1
        effective_res_addr = self.data_memory[res_addr] + offset2
        
        # Получаем операнды
        operand1 = self.data_memory[effective_addr1]
        operand2 = self.data_memory[addr2]
        
        # Выполняем операцию >=
        result = 1 if operand1 >= operand2 else 0
        
        # Сохраняем результат
        self.data_memory[effective_res_addr] = result
        
        # Перемещаем PC на 13 байт
        self.pc += 13
        
        return f"GTE: [{effective_res_addr}] = ({operand1} >= {operand2}) = {result}"
    
    def step(self) -> str:
        """Выполнение одной команды"""
        if self.pc >= len(self.code_memory):
            return None  # Программа завершена
        
        # Читаем код операции
        opcode = self.read_bits(0, 7)
        
        # Выполняем соответствующую команду
        if opcode == 111:
            return self.execute_load_const()
        elif opcode == 40:
            return self.execute_read_mem()
        elif opcode == 101:
            return self.execute_write_mem()
        elif opcode == 68:
            return self.execute_gte()
        else:
            raise ValueError(f"Неизвестный код операции: {opcode} на позиции {self.pc}")
    
    def run(self, verbose=False):
        """Выполнение всей программы"""
        step_count = 0
        while self.pc < len(self.code_memory):
            result = self.step()
            if result is None:
                break
            step_count += 1
            if verbose:
                print(f"Шаг {step_count}: {result}")
        
        if verbose:
            print(f"\nВыполнено {step_count} команд")
    
    def dump_memory_xml(self, filename: str, start_addr: int, end_addr: int):
        """Сохранение дампа памяти в XML"""
        root = ET.Element('memory_dump')
        root.set('start_address', str(start_addr))
        root.set('end_address', str(end_addr))
        
        for addr in range(start_addr, end_addr + 1):
            if addr < len(self.data_memory):
                cell = ET.SubElement(root, 'cell')
                cell.set('address', str(addr))
                cell.set('value', str(self.data_memory[addr]))
        
        # Форматируем XML для читаемости
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')
        
        # Записываем в файл
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)


def main():
    if len(sys.argv) < 5:
        print("Использование: python interpreter.py <бинарный_файл.bin> <выходной_дамп.xml> <начальный_адрес> <конечный_адрес>")
        sys.exit(1)
    
    binary_file = sys.argv[1]
    output_xml = sys.argv[2]
    start_addr = int(sys.argv[3])
    end_addr = int(sys.argv[4])
    
    # Чтение бинарного файла
    try:
        with open(binary_file, 'rb') as f:
            binary_code = f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл '{binary_file}' не найден", file=sys.stderr)
        sys.exit(1)
    
    print(f"Загружено {len(binary_code)} байт программы")
    
    # Создание и запуск виртуальной машины
    vm = VirtualMachine()
    vm.load_program(binary_code)
    
    print("Выполнение программы...\n")
    vm.run(verbose=True)
    
    # Сохранение дампа памяти
    print(f"\nСохранение дампа памяти ({start_addr}-{end_addr}) в {output_xml}")
    vm.dump_memory_xml(output_xml, start_addr, end_addr)
    
    print("Готово!")


if __name__ == '__main__':
    main()
