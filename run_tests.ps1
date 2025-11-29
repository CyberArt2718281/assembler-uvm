# Скрипт для запуска всех тестов
$python = "C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe"

Write-Host "=== Компиляция и выполнение test_vectors_1 ===" -ForegroundColor Green
& $python assembler.py tests\test_vectors_1.asm results\test_vectors_1.bin
& $python interpreter.py results\test_vectors_1.bin results\test_vectors_1_memory.xml 100 210

Write-Host "`n=== Компиляция и выполнение test_vectors_2 ===" -ForegroundColor Green
& $python assembler.py tests\test_vectors_2.asm results\test_vectors_2.bin
& $python interpreter.py results\test_vectors_2.bin results\test_vectors_2_memory.xml 100 210

Write-Host "`n=== Компиляция и выполнение test_vectors_3 ===" -ForegroundColor Green
& $python assembler.py tests\test_vectors_3.asm results\test_vectors_3.bin
& $python interpreter.py results\test_vectors_3.bin results\test_vectors_3_memory.xml 100 210

Write-Host "`n=== Все тесты выполнены ===" -ForegroundColor Green
