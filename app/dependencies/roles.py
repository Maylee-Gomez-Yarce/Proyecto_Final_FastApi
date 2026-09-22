from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.usuario import Usuario


def require_role(required_role: str):
    """
    Crea una dependencia que exige un rol específico.

    Si el usuario no está autenticado, get_current_user
    se encarga de devolver 401.

    Si está autenticado pero tiene otro rol, devuelve 403.
    """

    def role_dependency(
        usuario: Usuario = Depends(get_current_user),
    ) -> Usuario:

        if usuario.rol != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Acceso no permitido. "
                    f"Se requiere el rol '{required_role}'."
                ),
            )

        return usuario

    return role_dependency


def require_paciente(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    """
    Permite el acceso únicamente a usuarios con rol paciente.
    """

    if usuario.rol != "paciente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso permitido únicamente a pacientes.",
        )

    return usuario


def require_medico(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    """
    Permite el acceso únicamente a usuarios con rol médico.
    """

    if usuario.rol != "medico":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso permitido únicamente a médicos.",
        )

    return usuario
