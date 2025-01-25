import unittest
from unittest.mock import MagicMock 
from src.clientes import Clientes
from src.validations import validate_email

class TestClientes(unittest.TestCase):

    def setUp(self):
        # Crear un mock de la base de datos
        self.mock_db = MagicMock() 
        self.clientes = Clientes(self.mock_db)

    def test_valid_email(self):
        # Emails válidos
        self.assertTrue(validate_email("user@example.com"))
        self.assertTrue(validate_email("user.name+alias@sub.example.co.uk"))

    def test_invalid_email(self):
        # Emails inválidos
        self.assertFalse(validate_email("userexample.com"))  # Falta @
        self.assertFalse(validate_email("user@com"))         # Dominio inválido
        self.assertFalse(validate_email("user@.com"))        # Dominio vacío
        self.assertFalse(validate_email("user@domain.c"))    # TLD muy corto

    def test_agregar_cliente_con_email_valido(self):
        # Datos válidos
        resultado = self.clientes.agregar_cliente(
            "Juan", "Pérez", "Bogotá", "juan@example.com", "1234567890", "Privado"
        )
        self.mock_db.add_client_db.assert_called_once()  # Verifica que se llamó a la DB
        self.assertIsNone(resultado)  # Se espera que no retorne error

    def test_agregar_cliente_con_email_invalido(self):
        # Email inválido
        resultado = self.clientes.agregar_cliente(
            "Juan", "Pérez", "Bogotá", "juanexample.com", "1234567890", "Privado"
        )
        self.assertEqual(resultado, "Error: Email inválido. Formato no válido.")
        self.mock_db.add_client_db.assert_not_called()  # No debería llamar a la DB

    def test_agregar_cliente_sin_campos_obligatorios(self):
        # Faltan campos obligatorios
        resultado = self.clientes.agregar_cliente(
            "", "Pérez", "Bogotá", "juan@example.com", "1234567890", "Privado"
        )
        self.assertEqual(resultado, "Error: Nombre, Apellido, Ciudad y Tipo son obligatorios")
        self.mock_db.add_client_db.assert_not_called()  # No debería llamar a la DB

    def test_agregar_cliente_con_telefono_invalido(self):
        # Teléfono con caracteres no numéricos
        resultado = self.clientes.agregar_cliente(
            "Juan", "Pérez", "Bogotá", "juan@example.com", "123abc", "Regular"
        )
        self.assertEqual(resultado, "Error: Teléfono inválido. Debe contener solo números")
        self.mock_db.add_client_db.assert_not_called()  # No debería llamar a la DB

    def test_agregar_cliente_email_opcional(self):
        # Email opcional (campo vacío)
        resultado = self.clientes.agregar_cliente(
            "Juan", "Pérez", "Bogotá", "", "1234567890", "Regular"
        )
        self.mock_db.add_client_db.assert_called_once()  # Verifica que se llamó a la DB
        self.assertIsNone(resultado)  # Se espera que no retorne error

