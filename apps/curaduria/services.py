"""Servicios de dominio de la app curaduria.

Aquí vivirán aprobar_registro() y devolver_registro(): validan la
transición, comprueban el rol, crean la Revision y cambian el estado del
Registro, todo en una transacción (ver docs/arquitectura.md). El revisor
no corrige el contenido (RN-03): el servicio solo cambia el estado.
"""
